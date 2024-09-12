-- Purpose: Add unique constraint to resource_entry table so it can work with on-conflict
alter table resource_entry add constraint resource_type_id unique (resource_type, resource_id);

-- Purpose: Allow null values for pseudonym column, as not all data needs to be constrained to a pseudonym
alter table resource_entry alter column pseudonym drop not null;


