CREATE TABLE fhir_resources (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    resource_type varchar(64) NOT NULL,
    resource_id varchar(256) NOT NULL,
    resource jsonb NOT NULL
);

CREATE TABLE fhir_references (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    pseudonym uuid NOT NULL,
    references jsonb NOT NULL
);