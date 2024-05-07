
--- Create web user metadata
CREATE ROLE metadata;
ALTER ROLE metadata WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS ;

--- Create DBA role
CREATE ROLE metadata_dba;
ALTER ROLE metadata_dba WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION NOBYPASSRLS ;

CREATE TABLE deploy_releases
(
        version varchar(255),
        deployed_at timestamp default now()
);

ALTER TABLE deploy_releases OWNER TO metadata_dba;

GRANT SELECT ON deploy_releases TO metadata;


