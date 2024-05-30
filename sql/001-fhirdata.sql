CREATE TABLE fhir_resources (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    pseudonym uuid NOT NULL,
    resource_type varchar(64) NOT NULL,
    resource_id varchar(256) NOT NULL,
    resource jsonb NOT NULL
);