--
-- PostgreSQL database dump
--

-- Dumped from database version 11.9
-- Dumped by pg_dump version 13.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_stat_statements WITH SCHEMA public;


--
-- Name: EXTENSION pg_stat_statements; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_stat_statements IS 'track execution statistics of all SQL statements executed';


--
-- Name: apikey_status; Type: TYPE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE TYPE public.apikey_status AS ENUM (
    'active',
    'standby',
    'invalid'
);


ALTER TYPE public.apikey_status OWNER TO cloudsqlsuperuser;

--
-- Name: caption_status; Type: TYPE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE TYPE public.caption_status AS ENUM (
    'acquired',
    'unavailable',
    'queued',
    'error'
);


ALTER TYPE public.caption_status OWNER TO cloudsqlsuperuser;

--
-- Name: page_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.page_status AS ENUM (
    'queued',
    'acquired',
    'unavailable',
    'error'
);


ALTER TYPE public.page_status OWNER TO postgres;

SET default_tablespace = '';

--
-- Name: User; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."User" (
    id integer NOT NULL,
    username character varying,
    email character varying,
    password bytea
);


ALTER TABLE public."User" OWNER TO postgres;

--
-- Name: User_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public."User_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public."User_id_seq" OWNER TO postgres;

--
-- Name: User_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public."User_id_seq" OWNED BY public."User".id;


--
-- Name: active_storage_attachments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.active_storage_attachments (
    id bigint NOT NULL,
    name character varying NOT NULL,
    record_type character varying NOT NULL,
    record_id bigint NOT NULL,
    blob_id bigint NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.active_storage_attachments OWNER TO postgres;

--
-- Name: active_storage_attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.active_storage_attachments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.active_storage_attachments_id_seq OWNER TO postgres;

--
-- Name: active_storage_attachments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.active_storage_attachments_id_seq OWNED BY public.active_storage_attachments.id;


--
-- Name: active_storage_blobs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.active_storage_blobs (
    id bigint NOT NULL,
    key character varying NOT NULL,
    filename character varying NOT NULL,
    content_type character varying,
    metadata text,
    byte_size bigint NOT NULL,
    checksum character varying NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.active_storage_blobs OWNER TO postgres;

--
-- Name: active_storage_blobs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.active_storage_blobs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.active_storage_blobs_id_seq OWNER TO postgres;

--
-- Name: active_storage_blobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.active_storage_blobs_id_seq OWNED BY public.active_storage_blobs.id;


--
-- Name: apikeys; Type: TABLE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE TABLE public.apikeys (
    id integer NOT NULL,
    apikey character varying,
    status public.apikey_status DEFAULT 'active'::public.apikey_status,
    email character varying,
    standby_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.apikeys OWNER TO cloudsqlsuperuser;

--
-- Name: apikeys_id_seq; Type: SEQUENCE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE SEQUENCE public.apikeys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.apikeys_id_seq OWNER TO cloudsqlsuperuser;

--
-- Name: apikeys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloudsqlsuperuser
--

ALTER SEQUENCE public.apikeys_id_seq OWNED BY public.apikeys.id;


--
-- Name: ar_internal_metadata; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ar_internal_metadata (
    key character varying NOT NULL,
    value character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.ar_internal_metadata OWNER TO postgres;

--
-- Name: augment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.augment (
    id integer NOT NULL,
    video_id character(11),
    tsv tsvector,
    tsv_lemma tsvector,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.augment OWNER TO postgres;

--
-- Name: augment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.augment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.augment_id_seq OWNER TO postgres;

--
-- Name: augment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.augment_id_seq OWNED BY public.augment.id;


--
-- Name: caption; Type: TABLE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE TABLE public.caption (
    id integer NOT NULL,
    video_id character(11),
    status public.caption_status DEFAULT 'queued'::public.caption_status,
    caption character varying,
    wordcount integer,
    processed_at timestamp with time zone,
    caption_url character varying,
    caption_type character varying
);


ALTER TABLE public.caption OWNER TO cloudsqlsuperuser;

--
-- Name: caption_id_seq; Type: SEQUENCE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE SEQUENCE public.caption_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.caption_id_seq OWNER TO cloudsqlsuperuser;

--
-- Name: caption_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloudsqlsuperuser
--

ALTER SEQUENCE public.caption_id_seq OWNED BY public.caption.id;


--
-- Name: channel; Type: TABLE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE TABLE public.channel (
    id integer NOT NULL,
    channel_id character varying(24),
    title character varying,
    description character varying,
    country character varying,
    custom_url character varying,
    thumbnail character varying,
    created_at timestamp with time zone,
    retrieved_at timestamp with time zone,
    origin character varying,
    has_related boolean DEFAULT false,
    show_related character varying,
    activity_score double precision DEFAULT 0,
    activity character varying DEFAULT 'active'::character varying,
    rss_next_parsing timestamp with time zone DEFAULT now()
);


ALTER TABLE public.channel OWNER TO cloudsqlsuperuser;

--
-- Name: channel_id_seq; Type: SEQUENCE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE SEQUENCE public.channel_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.channel_id_seq OWNER TO cloudsqlsuperuser;

--
-- Name: channel_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloudsqlsuperuser
--

ALTER SEQUENCE public.channel_id_seq OWNED BY public.channel.id;


--
-- Name: channel_stat; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.channel_stat (
    id integer NOT NULL,
    channel_id character(24) NOT NULL,
    views bigint DEFAULT 0,
    subscribers integer DEFAULT 0,
    videos integer DEFAULT 0,
    retrieved_at timestamp with time zone
);


ALTER TABLE public.channel_stat OWNER TO postgres;

--
-- Name: channel_stat_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.channel_stat_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.channel_stat_id_seq OWNER TO postgres;

--
-- Name: channel_stat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.channel_stat_id_seq OWNED BY public.channel_stat.id;


--
-- Name: collection_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collection_items (
    id bigint NOT NULL,
    collection_id bigint,
    video_id character varying(11),
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    search_id bigint,
    channel_id character varying,
    origin character varying
);


ALTER TABLE public.collection_items OWNER TO postgres;

--
-- Name: collection_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collection_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.collection_items_id_seq OWNER TO postgres;

--
-- Name: collection_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collection_items_id_seq OWNED BY public.collection_items.id;


--
-- Name: collections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.collections (
    id bigint NOT NULL,
    title character varying,
    description character varying,
    user_id integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.collections OWNER TO postgres;

--
-- Name: collections_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.collections_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.collections_id_seq OWNER TO postgres;

--
-- Name: collections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.collections_id_seq OWNED BY public.collections.id;


--
-- Name: comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comments (
    id bigint NOT NULL,
    comment_id character varying,
    video_id character varying,
    discussion_id character varying,
    parent_id character varying,
    author_name character varying,
    author_channel_id character varying,
    text character varying,
    reply_count integer,
    like_count integer,
    published_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.comments OWNER TO postgres;

--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comments_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.comments_id_seq OWNER TO postgres;

--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: discussions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.discussions (
    id bigint NOT NULL,
    video_id character varying,
    total_results integer,
    results_per_page integer,
    error character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.discussions OWNER TO postgres;

--
-- Name: discussions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.discussions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.discussions_id_seq OWNER TO postgres;

--
-- Name: discussions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.discussions_id_seq OWNED BY public.discussions.id;


--
-- Name: export_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.export_items (
    id bigint NOT NULL,
    export_id character varying,
    title character varying,
    filesize integer,
    nrows integer,
    ncolumns integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.export_items OWNER TO postgres;

--
-- Name: export_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.export_items_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.export_items_id_seq OWNER TO postgres;

--
-- Name: export_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.export_items_id_seq OWNED BY public.export_items.id;


--
-- Name: exports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exports (
    id bigint NOT NULL,
    collection_id character varying,
    title character varying,
    description character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.exports OWNER TO postgres;

--
-- Name: exports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exports_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.exports_id_seq OWNER TO postgres;

--
-- Name: exports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exports_id_seq OWNED BY public.exports.id;


--
-- Name: flow; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.flow (
    id integer NOT NULL,
    channel_id character(24),
    video_id character(11),
    flowname character varying NOT NULL,
    start_at timestamp with time zone,
    mode character varying DEFAULT 'organic'::character varying
);


ALTER TABLE public.flow OWNER TO postgres;

--
-- Name: flow_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.flow_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.flow_id_seq OWNER TO postgres;

--
-- Name: flow_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.flow_id_seq OWNED BY public.flow.id;


--
-- Name: helm; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.helm (
    id integer NOT NULL,
    jobname character varying NOT NULL,
    count_ integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.helm OWNER TO postgres;

--
-- Name: helm_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.helm_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.helm_id_seq OWNER TO postgres;

--
-- Name: helm_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.helm_id_seq OWNED BY public.helm.id;


--
-- Name: pipeline; Type: TABLE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE TABLE public.pipeline (
    id integer NOT NULL,
    video_id character(11),
    channel_id character(24),
    lang character varying(10),
    status character varying DEFAULT 'incomplete'::character varying,
    created_at timestamp with time zone DEFAULT now(),
    lang_conf double precision
);


ALTER TABLE public.pipeline OWNER TO cloudsqlsuperuser;

--
-- Name: pipeline_id_seq; Type: SEQUENCE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE SEQUENCE public.pipeline_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pipeline_id_seq OWNER TO cloudsqlsuperuser;

--
-- Name: pipeline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloudsqlsuperuser
--

ALTER SEQUENCE public.pipeline_id_seq OWNED BY public.pipeline.id;


--
-- Name: query; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.query (
    id integer NOT NULL,
    sql character varying NOT NULL,
    queryname character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    active boolean DEFAULT true
);


ALTER TABLE public.query OWNER TO postgres;

--
-- Name: query_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.query_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.query_id_seq OWNER TO postgres;

--
-- Name: query_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.query_id_seq OWNED BY public.query.id;


--
-- Name: related_channels; Type: TABLE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE TABLE public.related_channels (
    id integer NOT NULL,
    channel_id character varying,
    related_id character varying,
    retrieved_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.related_channels OWNER TO cloudsqlsuperuser;

--
-- Name: related_channels_id_seq; Type: SEQUENCE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE SEQUENCE public.related_channels_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.related_channels_id_seq OWNER TO cloudsqlsuperuser;

--
-- Name: related_channels_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloudsqlsuperuser
--

ALTER SEQUENCE public.related_channels_id_seq OWNED BY public.related_channels.id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.schema_migrations (
    version character varying NOT NULL
);


ALTER TABLE public.schema_migrations OWNER TO postgres;

--
-- Name: searches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.searches (
    id bigint NOT NULL,
    query json,
    collection_id bigint,
    keywords character varying,
    "on" character varying,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    behavior character varying DEFAULT 'static'::character varying
);


ALTER TABLE public.searches OWNER TO postgres;

--
-- Name: searches_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.searches_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.searches_id_seq OWNER TO postgres;

--
-- Name: searches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.searches_id_seq OWNED BY public.searches.id;


--
-- Name: topic; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.topic (
    id integer NOT NULL,
    channel_id character(24),
    topics json,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.topic OWNER TO postgres;

--
-- Name: topic_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.topic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.topic_id_seq OWNER TO postgres;

--
-- Name: topic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.topic_id_seq OWNED BY public.topic.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id bigint NOT NULL,
    email character varying DEFAULT ''::character varying NOT NULL,
    encrypted_password character varying DEFAULT ''::character varying NOT NULL,
    reset_password_token character varying,
    reset_password_sent_at timestamp without time zone,
    remember_created_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: video; Type: TABLE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE TABLE public.video (
    id integer NOT NULL,
    video_id character(11),
    channel_id character(24),
    title character varying,
    summary character varying,
    thumbnail character varying,
    category_id integer,
    duration character varying,
    privacy_status character varying,
    caption boolean DEFAULT false,
    published_at timestamp with time zone,
    retrieved_at timestamp with time zone,
    tags character varying,
    origin character varying,
    footer character varying,
    pubdate character(10),
    live_content character varying,
    default_audio_language character varying,
    default_language character varying,
    seconds integer,
    wikitopics character varying
);


ALTER TABLE public.video OWNER TO cloudsqlsuperuser;

--
-- Name: video_id_seq; Type: SEQUENCE; Schema: public; Owner: cloudsqlsuperuser
--

CREATE SEQUENCE public.video_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.video_id_seq OWNER TO cloudsqlsuperuser;

--
-- Name: video_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cloudsqlsuperuser
--

ALTER SEQUENCE public.video_id_seq OWNED BY public.video.id;


--
-- Name: video_recommendations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.video_recommendations (
    id integer NOT NULL,
    src_video_id character(11),
    tgt_video_id character(11),
    harvest_date character varying,
    tgt_video_harvested_at timestamp with time zone
);


ALTER TABLE public.video_recommendations OWNER TO postgres;

--
-- Name: video_recommendations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.video_recommendations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.video_recommendations_id_seq OWNER TO postgres;

--
-- Name: video_recommendations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.video_recommendations_id_seq OWNED BY public.video_recommendations.id;


--
-- Name: video_scrape; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.video_scrape (
    id integer NOT NULL,
    video_id character(11),
    completed_date character(10) DEFAULT NULL::bpchar,
    scraped_date character(10) DEFAULT NULL::bpchar,
    scrape_result character varying,
    downloaded_date character(10) DEFAULT NULL::bpchar,
    recos_count integer,
    captions character varying,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.video_scrape OWNER TO postgres;

--
-- Name: video_scrape_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.video_scrape_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.video_scrape_id_seq OWNER TO postgres;

--
-- Name: video_scrape_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.video_scrape_id_seq OWNED BY public.video_scrape.id;


--
-- Name: video_stat; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.video_stat (
    id integer NOT NULL,
    video_id character(11),
    source character(3) DEFAULT 'rss'::bpchar,
    views integer DEFAULT 0,
    viewed_at character(10) NOT NULL,
    like_count integer,
    dislike_count integer,
    favorite_count integer,
    comment_count integer
);


ALTER TABLE public.video_stat OWNER TO postgres;

--
-- Name: video_stat_02_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.video_stat_02_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.video_stat_02_id_seq OWNER TO postgres;

--
-- Name: video_stat_02_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.video_stat_02_id_seq OWNED BY public.video_stat.id;


--
-- Name: yt_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.yt_categories (
    id integer NOT NULL,
    category_id integer NOT NULL,
    category character varying NOT NULL,
    assignable boolean
);


ALTER TABLE public.yt_categories OWNER TO postgres;

--
-- Name: yt_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.yt_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.yt_categories_id_seq OWNER TO postgres;

--
-- Name: yt_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.yt_categories_id_seq OWNED BY public.yt_categories.id;


--
-- Name: User id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."User" ALTER COLUMN id SET DEFAULT nextval('public."User_id_seq"'::regclass);


--
-- Name: active_storage_attachments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.active_storage_attachments ALTER COLUMN id SET DEFAULT nextval('public.active_storage_attachments_id_seq'::regclass);


--
-- Name: active_storage_blobs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.active_storage_blobs ALTER COLUMN id SET DEFAULT nextval('public.active_storage_blobs_id_seq'::regclass);


--
-- Name: apikeys id; Type: DEFAULT; Schema: public; Owner: cloudsqlsuperuser
--

ALTER TABLE ONLY public.apikeys ALTER COLUMN id SET DEFAULT nextval('public.apikeys_id_seq'::regclass);


--
-- Name: augment id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.augment ALTER COLUMN id SET DEFAULT nextval('public.augment_id_seq'::regclass);


--
-- Name: caption id; Type: DEFAULT; Schema: public; Owner: cloudsqlsuperuser
--

ALTER TABLE ONLY public.caption ALTER COLUMN id SET DEFAULT nextval('public.caption_id_seq'::regclass);


--
-- Name: channel id; Type: DEFAULT; Schema: public; Owner: cloudsqlsuperuser
--

ALTER TABLE ONLY public.channel ALTER COLUMN id SET DEFAULT nextval('public.channel_id_seq'::regclass);


--
-- Name: channel_stat id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.channel_stat ALTER COLUMN id SET DEFAULT nextval('public.channel_stat_id_seq'::regclass);


--
-- Name: collection_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_items ALTER COLUMN id SET DEFAULT nextval('public.collection_items_id_seq'::regclass);


--
-- Name: collections id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections ALTER COLUMN id SET DEFAULT nextval('public.collections_id_seq'::regclass);


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: discussions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.discussions ALTER COLUMN id SET DEFAULT nextval('public.discussions_id_seq'::regclass);


--
-- Name: export_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.export_items ALTER COLUMN id SET DEFAULT nextval('public.export_items_id_seq'::regclass);


--
-- Name: exports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exports ALTER COLUMN id SET DEFAULT nextval('public.exports_id_seq'::regclass);


--
-- Name: flow id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.flow ALTER COLUMN id SET DEFAULT nextval('public.flow_id_seq'::regclass);


--
-- Name: helm id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.helm ALTER COLUMN id SET DEFAULT nextval('public.helm_id_seq'::regclass);


--
-- Name: pipeline id; Type: DEFAULT; Schema: public; Owner: cloudsqlsuperuser
--

ALTER TABLE ONLY public.pipeline ALTER COLUMN id SET DEFAULT nextval('public.pipeline_id_seq'::regclass);


--
-- Name: query id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.query ALTER COLUMN id SET DEFAULT nextval('public.query_id_seq'::regclass);


--
-- Name: related_channels id; Type: DEFAULT; Schema: public; Owner: cloudsqlsuperuser
--

ALTER TABLE ONLY public.related_channels ALTER COLUMN id SET DEFAULT nextval('public.related_channels_id_seq'::regclass);


--
-- Name: searches id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.searches ALTER COLUMN id SET DEFAULT nextval('public.searches_id_seq'::regclass);


--
-- Name: topic id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topic ALTER COLUMN id SET DEFAULT nextval('public.topic_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: video id; Type: DEFAULT; Schema: public; Owner: cloudsqlsuperuser
--

ALTER TABLE ONLY public.video ALTER COLUMN id SET DEFAULT nextval('public.video_id_seq'::regclass);


--
-- Name: video_recommendations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.video_recommendations ALTER COLUMN id SET DEFAULT nextval('public.video_recommendations_id_seq'::regclass);


--
-- Name: video_scrape id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.video_scrape ALTER COLUMN id SET DEFAULT nextval('public.video_scrape_id_seq'::regclass);


--
-- Name: video_stat id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.video_stat ALTER COLUMN id SET DEFAULT nextval('public.video_stat_02_id_seq'::regclass);


--
-- Name: yt_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.yt_categories ALTER COLUMN id SET DEFAULT nextval('public.yt_categories_id_seq'::regclass);


--
-- Name: User User_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT "User_email_key" UNIQUE (email);


--
-- Name: User User_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT "User_pkey" PRIMARY KEY (id);


--
-- Name: User User_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."User"
    ADD CONSTRAINT "User_username_key" UNIQUE (username);


--
-- Name: active_storage_attachments active_storage_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.active_storage_attachments
    ADD CONSTRAINT active_storage_attachments_pkey PRIMARY KEY (id);


--
-- Name: active_storage_blobs active_storage_blobs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.active_storage_blobs
    ADD CONSTRAINT active_storage_blobs_pkey PRIMARY KEY (id);


--
-- Name: ar_internal_metadata ar_internal_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ar_internal_metadata
    ADD CONSTRAINT ar_internal_metadata_pkey PRIMARY KEY (key);


--
-- Name: collection_items collection_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collection_items
    ADD CONSTRAINT collection_items_pkey PRIMARY KEY (id);


--
-- Name: collections collections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.collections
    ADD CONSTRAINT collections_pkey PRIMARY KEY (id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: discussions discussions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.discussions
    ADD CONSTRAINT discussions_pkey PRIMARY KEY (id);


--
-- Name: export_items export_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.export_items
    ADD CONSTRAINT export_items_pkey PRIMARY KEY (id);


--
-- Name: exports exports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exports
    ADD CONSTRAINT exports_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: searches searches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.searches
    ADD CONSTRAINT searches_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: augment_tsv_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX augment_tsv_idx ON public.augment USING gin (tsv);


--
-- Name: augment_tsv_lemma_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX augment_tsv_lemma_idx ON public.augment USING gin (tsv_lemma);


--
-- Name: augment_video_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX augment_video_id ON public.augment USING btree (video_id);


--
-- Name: channel_origin; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE INDEX channel_origin ON public.channel USING btree (origin);


--
-- Name: channel_stat_channel_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX channel_stat_channel_id ON public.channel_stat USING btree (channel_id);


--
-- Name: helm_jobname; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX helm_jobname ON public.helm USING btree (jobname);


--
-- Name: idx_video_channel_id; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE INDEX idx_video_channel_id ON public.video USING btree (channel_id);


--
-- Name: index_active_storage_attachments_on_blob_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_active_storage_attachments_on_blob_id ON public.active_storage_attachments USING btree (blob_id);


--
-- Name: index_active_storage_attachments_uniqueness; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX index_active_storage_attachments_uniqueness ON public.active_storage_attachments USING btree (record_type, record_id, name, blob_id);


--
-- Name: index_active_storage_blobs_on_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX index_active_storage_blobs_on_key ON public.active_storage_blobs USING btree (key);


--
-- Name: index_collection_items_on_channel_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_collection_items_on_channel_id ON public.collection_items USING btree (channel_id);


--
-- Name: index_collection_items_on_channel_id_and_collection_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX index_collection_items_on_channel_id_and_collection_id ON public.collection_items USING btree (channel_id, collection_id);


--
-- Name: index_collection_items_on_collection_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_collection_items_on_collection_id ON public.collection_items USING btree (collection_id);


--
-- Name: index_collection_items_on_search_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_collection_items_on_search_id ON public.collection_items USING btree (search_id);


--
-- Name: index_collection_items_on_video_id_and_collection_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX index_collection_items_on_video_id_and_collection_id ON public.collection_items USING btree (video_id, collection_id);


--
-- Name: index_comments_on_comment_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX index_comments_on_comment_id ON public.comments USING btree (comment_id);


--
-- Name: index_comments_on_discussion_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_comments_on_discussion_id ON public.comments USING btree (discussion_id);


--
-- Name: index_comments_on_video_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_comments_on_video_id ON public.comments USING btree (video_id);


--
-- Name: index_discussions_on_video_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX index_discussions_on_video_id ON public.discussions USING btree (video_id);


--
-- Name: index_export_items_on_export_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_export_items_on_export_id ON public.export_items USING btree (export_id);


--
-- Name: index_exports_on_collection_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_exports_on_collection_id ON public.exports USING btree (collection_id);


--
-- Name: index_searches_on_collection_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX index_searches_on_collection_id ON public.searches USING btree (collection_id);


--
-- Name: index_users_on_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX index_users_on_email ON public.users USING btree (email);


--
-- Name: index_users_on_reset_password_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX index_users_on_reset_password_token ON public.users USING btree (reset_password_token);


--
-- Name: index_video_on_category_id; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE INDEX index_video_on_category_id ON public.video USING btree (category_id);


--
-- Name: src_video_video_recommendations; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX src_video_video_recommendations ON public.video_recommendations USING btree (src_video_id);


--
-- Name: tgt_video_video_recommendations; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tgt_video_video_recommendations ON public.video_recommendations USING btree (tgt_video_id);


--
-- Name: topic_channel_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX topic_channel_id ON public.topic USING btree (channel_id);


--
-- Name: unique_caption_id; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE UNIQUE INDEX unique_caption_id ON public.caption USING btree (video_id);


--
-- Name: unique_channel_flow; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX unique_channel_flow ON public.flow USING btree (channel_id, flowname);


--
-- Name: unique_channel_id; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE UNIQUE INDEX unique_channel_id ON public.channel USING btree (channel_id);


--
-- Name: unique_piepline_channel_id; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE UNIQUE INDEX unique_piepline_channel_id ON public.pipeline USING btree (channel_id);


--
-- Name: unique_pipeline_video_id; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE UNIQUE INDEX unique_pipeline_video_id ON public.pipeline USING btree (video_id);


--
-- Name: unique_queryname; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX unique_queryname ON public.query USING btree (queryname);


--
-- Name: unique_related_channel_id; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE UNIQUE INDEX unique_related_channel_id ON public.related_channels USING btree (channel_id, related_id);


--
-- Name: unique_vid_recommendation_src_tgt_date_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX unique_vid_recommendation_src_tgt_date_id ON public.video_recommendations USING btree (src_video_id, tgt_video_id, harvest_date);


--
-- Name: unique_video_flow; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX unique_video_flow ON public.flow USING btree (video_id, flowname);


--
-- Name: unique_video_id; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE UNIQUE INDEX unique_video_id ON public.video USING btree (video_id);


--
-- Name: unique_video_stat; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX unique_video_stat ON public.video_stat USING btree (video_id, viewed_at);


--
-- Name: video_origin; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE INDEX video_origin ON public.video USING btree (origin);


--
-- Name: video_published_at; Type: INDEX; Schema: public; Owner: cloudsqlsuperuser
--

CREATE INDEX video_published_at ON public.video USING btree (published_at);


--
-- Name: video_scrape_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX video_scrape_id ON public.video_scrape USING btree (video_id);


--
-- Name: active_storage_attachments fk_rails_c3b3935057; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.active_storage_attachments
    ADD CONSTRAINT fk_rails_c3b3935057 FOREIGN KEY (blob_id) REFERENCES public.active_storage_blobs(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: cloudsqlsuperuser
--

REVOKE ALL ON SCHEMA public FROM cloudsqladmin;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO cloudsqlsuperuser;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

