'''
1. Capture list of videos from collections (defined by channels)
without captions
2. for each batch of videos
'''

import numpy as np
import pandas as pd
import os, re, json, csv, sys
import datetime, time
from tqdm import tqdm
from py import *
import glob


def capture_captions(video_id):
    start_ = 'https://www.youtube.com/api/timedtext'
    end_ = '",'

    HTML_TAG_REGEX = re.compile(r'<[^>]*>', re.IGNORECASE)

    http_client = requests.Session()
    text        = http_client.get('https://www.youtube.com/watch?v=' + video_id).text.replace('\\u0026', '&').replace('\\', '')
    m = re.findall('{}(.+?){}'.format(start_, end_), text)
    captions = []

    for u in m:
        url = start_+u
        if Caption.get_lang(start_+url) == 'fr':
            result = requests.Session().get(url)
            captions_text = result.text
            if (len(captions_text) > 0) and (result.status_code == 200):
                captext = [ re.sub(HTML_TAG_REGEX, '', html.unescape(xml_element.text)).replace("\n",' ').replace("\'","'")
                            for xml_element in ElementTree.fromstring(captions_text)
                            if xml_element.text is not None ]
                captions.append({
                    'video_id': video_id,
                    'len_': len(result.text),
                    'text': ' '.join(captext)
                })
    if len(captions) > 0:
        return captions[0]['text']
    else:
        return None


if __name__ == '__main__':

    if False:
        '''
          Part 1: Export videos from collections with missing captions to csv
        '''
        # sql = '''select distinct(channel_id) from collection_items where collection_id in (13, 15, 20)'''
        sql = '''select distinct(channel_id) from collection_items where collection_id in (23)'''
        df = pd.read_sql(sql, job.db.conn)
        channel_count = df.shape[0]

        data = pd.DataFrame()
        offset, batch, limit = 0, 0, 500

        while offset < channel_count:
            sql = f'''
                select distinct v.channel_id, v.video_id
                from video v
                left join caption cap on cap.video_id = v.video_id
                where v.channel_id in (
                    select distinct(channel_id)
                    from collection_items
                    where collection_id in (23)
                    order by channel_id
                    limit {limit} offset {offset}
                )
                and cap.id is null
                order by v.channel_id, v.video_id
            '''
            data = pd.read_sql(sql, job.db.conn)
            data['process'] = ''
            data['error'] = ''
            data['found'] = 0

            filename = f"extended_wizzdeo_videos_no_caption_batch_{str(batch).zfill(2)}.csv"
            data.to_csv(os.path.join('./data/captions', filename), index = False)
            offset += limit
            batch  += 1
            print(f"- [{offset}] {data.shape[0]} {filename}")

    if True:
        '''
          Part 2: for each batch data file, for each channel, for each video
            - get caption file with youtube-dl
            - handle flow with df['process']
            - if captions: send to bucket/dataskat-kansatsu-captions/channel_id/
            - filename: {channel_id}_{video_id}_{timestamp}.
        '''
        caption_path = './data/captions/'
        files = sorted([filename for filename in glob.glob(f"{caption_path}videos_no_caption_batch_*.csv")])
        filename = files[15]
        print(f"== filename : {filename}")
        df = pd.read_csv(filename)

        df.fillna(value = {'found': 0}, inplace = True)
        df.fillna('', inplace = True)
        df['found'] = df.found.astype(int)
        # raise "stop"
        caption_count = 0
        channel_count = 0
        channel_ids = df.channel_id.unique()
        for channel_id in channel_ids:
            without = 0
            channel_count +=1
            print()
            print("==="*20)
            print(f"[{channel_count} / {len(channel_ids)}] \t{channel_id}")
            print("---"*20)
            local_output_path = os.path.join(caption_path, channel_id)
            if not os.path.exists(local_output_path):
                os.makedirs(local_output_path)
                print(f"- creating {local_output_path}")
            cond_remaining = (df.channel_id == channel_id) & (df.found == 0) & (df.error == '')
            video_ids = df[cond_remaining].video_id.unique()
            print(f"- {len(video_ids)} videos")
            print("---"*20)
            k = 0
            for video_id in tqdm(video_ids):
                cond = (df.channel_id == channel_id) & (df.video_id == video_id)
                k +=1
                if (video_id[0] != '-') & (without < 20):
                    time.sleep(np.random.randint( 4))
                    df.loc[cond,  'process'] = 'started ytdl'
                    if True:
                        try:
                            captext = capture_captions(video_id)
                            if captext is not None:
                                cap_file= f"{local_output_path}/{video_id}.txt"
                                with open(cap_file, 'w') as f:
                                    f.write(captext)
                                caption_count +=1
                                # print(f"new cap for {video_id}")
                        except:
                            df.loc[cond,'error'] = f"manual scraping failed"
                            print(f"***manual scraping failed***")
                            df.to_csv(filename, index = False, quoting = csv.QUOTE_ALL)



                    if False:
                        try:
                            print(f"[{k}/{len(video_ids)}]  wo:{without} \t {video_id}", end="\t")
                            cmd = f'''youtube-dl --write-auto-sub --sub-lang fr \
                                        --sub-format "srt/ass/best"  \
                                        --skip-download --quiet --no-warnings  \
                                        -o {local_output_path}/'%(id)s.%(ext)s' --ignore-errors \
                                        {video_id}
                                    '''
                            os.system(cmd)
                        except:
                            df.loc[cond,'error'] = f"cmd failed {cmd}"
                            print(f"***cmd failed***\n{cmd}")
                            df.to_csv(filename, index = False, quoting = csv.QUOTE_ALL)

                    if glob.glob(f"{local_output_path}/{video_id}.*"):
                        without = 0
                        cf = [f.split('/')[-1] for f in   glob.glob(f"{local_output_path}/{video_id}.*")]
                        # print(f"found: {cf}")
                        df.loc[cond,  'found'] = len(cf)
                        df.loc[cond,  'process'] = 'captions found'
                        df.to_csv(filename, index = False, quoting = csv.QUOTE_ALL)
                    else:
                        without +=1
                        df.loc[cond,  'process'] = 'no captions found'
                        df.to_csv(filename, index = False, quoting = csv.QUOTE_ALL)
                else:
                    df.loc[cond,  'process'] = 'skip video_id'
                    df.to_csv(filename, index = False, quoting = csv.QUOTE_ALL)

            print(f"== done with {channel_id}")
            time.sleep(5)
        print(f"== Found a total of {caption_count} captions")


            # capfiles = sorted([filename for filename in glob.glob(f"{local_output_path}/*.*")])
                # result = subprocess.run(cmd.split(), stdout=subprocess.PIPE).stdout.decode('utf-8')
                # TODO
                # find files in local_output_path
                # send to bucket
                # rm local_output_path
                # update df
                # save df
                # add try



# youtube-dl --write-auto-sub --sub-lang fr --sub-format "ass/srt/best"  --skip-download -o '%(id)s.%(ext)s' -v --ignore-errors PV5BW8P5H_U
#
#                 result = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
# youtube-dl --all-subs --skip-download -o '%(id)s.%(ext)s'-v --ignore-errors PV5BW8P5H_U
    if False:
        # given video_id, manual
        def capture_captions(video_id):
            start_ = 'https://www.youtube.com/api/timedtext'
            end_ = '",'

            HTML_TAG_REGEX = re.compile(r'<[^>]*>', re.IGNORECASE)

            http_client = requests.Session()
            text        = http_client.get('https://www.youtube.com/watch?v=' + video_id).text.replace('\\u0026', '&').replace('\\', '')
            m = re.findall('{}(.+?){}'.format(start_, end_), text)
            captions = []

            for u in m:
                url = start_+u
                if Caption.get_lang(start_+url) == 'fr':
                    result = requests.Session().get(url)
                    captions_text = result.text
                    if (len(captions_text) > min_len) and (result.status_code == 200):
                        captext = [ re.sub(HTML_TAG_REGEX, '', html.unescape(xml_element.text)).replace("\n",' ').replace("\'","'")
                                    for xml_element in ElementTree.fromstring(captions_text)
                                    if xml_element.text is not None ]
                        captions.append({
                            'video_id': video_id,
                            'len_': len(result.text),
                            'text': ' '.join(captext)
                        })
            return captions[0]['text']

    '''
    google cloud storage API examples
    '''
    if False:
        bucket = client.get_bucket('my-bucket-name')

        blob = storage.Blob('path/to/blob', bucket)
        # download file
        with open('file-to-download-to') as file_obj:
            client.download_blob_to_file('gs://bucket_name/path/to/blob', file_obj)

        # upload file
        blob = bucket.blob(bucketFolder + file)
        blob.upload_from_filename(localFile)

        # list files in bucket
        files = bucket.list_blobs()
        files = bucket.list_blobs(prefix=bucketFolder)

    # ----
