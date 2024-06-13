create table resource_entry
(
    id            uuid    default gen_random_uuid() not null
        constraint fhir_resources_pkey
            primary key,
    pseudonym     uuid                              not null,
    resource_type varchar(64)                       not null,
    resource_id   varchar(256)                      not null,
    resource      jsonb                             not null,
    version       integer default 1                 not null,
    created_dt    timestamp,
    deleted       boolean default false             not null
);
