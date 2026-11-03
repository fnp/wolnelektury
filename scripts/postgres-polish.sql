CREATE EXTENSION IF NOT EXISTS unaccent;

DO $$
  BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_ts_dict
               WHERE dictname = 'polish_hunspell'
                 AND dictnamespace = 'public'::regnamespace) THEN
    CREATE TEXT SEARCH DICTIONARY public.polish_hunspell (
        TEMPLATE = ispell, DictFile = polish, AffFile = polish
    );
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_ts_config
       	       WHERE cfgname = 'polish'
               AND cfgnamespace = 'public'::regnamespace) THEN
    CREATE TEXT SEARCH CONFIGURATION public.polish (COPY = pg_catalog.simple);
  END IF;
END $$;

ALTER TEXT SEARCH DICTIONARY public.polish_hunspell (
  DictFile = polish, AffFile = polish, StopWords
);

ALTER TEXT SEARCH CONFIGURATION public.polish
  ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
  WITH unaccent, polish_hunspell, simple;


