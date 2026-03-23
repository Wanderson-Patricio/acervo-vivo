
CREATE TABLE "Users"(
    "id" BIGSERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "cpf" VARCHAR(11) NOT NULL,
    "birth_date" DATE NOT NULL,
    "address_id" BIGINT NOT NULL,
    "contact_id" BIGINT NOT NULL,
    "role_id" BIGINT NOT NULL,
    "registration_timestamp" TIMESTAMP(0) WITH TIME zone NOT NULL
);
ALTER TABLE
    "Users" ADD PRIMARY KEY("id");


CREATE TABLE "Addresses"(
    "id" BIGSERIAL NOT NULL,
    "street" VARCHAR(255) NOT NULL,
    "number" SMALLINT NOT NULL,
    "complement" VARCHAR(255) NULL,
    "neighbourhood" VARCHAR(255) NOT NULL,
    "city" VARCHAR(50) NOT NULL,
    "state" VARCHAR(2) NOT NULL,
    "country" VARCHAR(50) NOT NULL,
    "zip_code" VARCHAR(8) NULL
);
ALTER TABLE
    "Addresses" ADD PRIMARY KEY("id");


CREATE TABLE "Contacts"(
    "id" BIGSERIAL NOT NULL,
    "phone_number" VARCHAR(13) NOT NULL,
    "email" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "Contacts" ADD PRIMARY KEY("id");


CREATE TABLE "Authentication"(
    "id" BIGSERIAL NOT NULL,
    "user_id" BIGINT NOT NULL,
    "hash_password" VARCHAR(255) NOT NULL,
    "last_time_altered" TIMESTAMP(0) WITH TIME zone NOT NULL,
    "is_blocked" BOOLEAN NOT NULL DEFAULT FALSE
);
ALTER TABLE
    "Authentication" ADD PRIMARY KEY("id");


CREATE TABLE "logs"(
    "id" BIGSERIAL NOT NULL,
    "created_at" TIMESTAMP(0) WITH TIME zone NOT NULL,
    "user_id" BIGINT NOT NULL,
    "endpoint" TEXT NOT NULL,
    "http_method" VARCHAR(10) NOT NULL,
    "status_code" SMALLINT NOT NULL,
    "level" VARCHAR(255) NOT NULL,
    "details" jsonb NULL,
    "message" BIGINT NOT NULL DEFAULT '""',
    "user_agent" TEXT NOT NULL,
    "ip_address" VARCHAR(15) NOT NULL
);
ALTER TABLE
    "logs" ADD PRIMARY KEY("id");


CREATE TABLE "Accesses"(
    "id" BIGSERIAL NOT NULL,
    "user_id" BIGINT NOT NULL,
    "login_timestamp" TIMESTAMP(0) WITH TIME zone NOT NULL,
    "ip_address" VARCHAR(15) NOT NULL,
    "user_agent" TEXT NOT NULL
);
ALTER TABLE
    "Accesses" ADD PRIMARY KEY("id");


CREATE TABLE "Roles"(
    "id" BIGSERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "access_level" BIGINT NOT NULL,
    "description" VARCHAR(255) NOT NULL
);
ALTER TABLE
    "Roles" ADD PRIMARY KEY("id");


CREATE TABLE "FamilyTrees"(
    "id" BIGSERIAL NOT NULL,
    "created_by" BIGINT NOT NULL,
    "created_at" TIMESTAMP(0) WITH TIME zone NOT NULL,
    "region_id" BIGINT NOT NULL
);
ALTER TABLE
    "FamilyTrees" ADD PRIMARY KEY("id");


CREATE TABLE "FamilyMembers"(
    "id" BIGSERIAL NOT NULL,
    "tree_id" BIGINT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "birth_date" DATE NOT NULL,
    "picture_id" BIGINT NULL,
    "father_id" BIGINT NULL,
    "mother_id" BIGINT NULL,
    "bibliography" TEXT NULL,
    "user_id" BIGINT NULL
);
ALTER TABLE
    "FamilyMembers" ADD PRIMARY KEY("id");


CREATE TABLE "Regions"(
    "id" BIGSERIAL NOT NULL,
    "neighbourhood" VARCHAR(255) NOT NULL,
    "city" VARCHAR(255) NOT NULL,
    "state" VARCHAR(2) NOT NULL,
    "country" VARCHAR(255) NOT NULL,
    "latitude" DECIMAL(8, 2) NOT NULL,
    "longitude" DECIMAL(8, 2) NOT NULL
);
ALTER TABLE
    "Regions" ADD PRIMARY KEY("id");


CREATE TABLE "FamilyTreePictures"(
    "id" BIGSERIAL NOT NULL,
    "picture_url" TEXT NOT NULL,
    "is_public" BOOLEAN NOT NULL DEFAULT FALSE
);
ALTER TABLE
    "FamilyTreePictures" ADD PRIMARY KEY("id");


CREATE TABLE "AcceptanceTerms"(
    "id" BIGSERIAL NOT NULL,
    "user_id" BIGINT NOT NULL,
    "acceptance_timestamp" TIMESTAMP(0) WITH TIME zone NOT NULL,
    "term_version" VARCHAR(255) NOT NULL,
    "ip_address" VARCHAR(15) NOT NULL,
    "user_agent" TEXT NOT NULL,
    "action_type" VARCHAR(50) NOT NULL,
    "is_active" BOOLEAN NOT NULL
);
ALTER TABLE
    "AcceptanceTerms" ADD PRIMARY KEY("id");


CREATE TABLE "Person"(
    "id" BIGSERIAL NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "birth_date" DATE NOT NULL,
    "death_date" DATE NULL,
    "occupation" TEXT NOT NULL,
    "life_details" TEXT NOT NULL,
    "region_id" BIGINT NOT NULL,
    "user_id" BIGINT NULL
);
ALTER TABLE
    "Person" ADD PRIMARY KEY("id");


CREATE TABLE "BibliographyPictures"(
    "id" BIGSERIAL NOT NULL,
    "picture_url" TEXT NOT NULL,
    "person_id" BIGINT NOT NULL,
    "is_main_picture" BOOLEAN NOT NULL DEFAULT FALSE
);
ALTER TABLE
    "BibliographyPictures" ADD PRIMARY KEY("id");


CREATE TABLE "Events"(
    "id" BIGSERIAL NOT NULL,
    "event_name" VARCHAR(255) NOT NULL,
    "event_description" TEXT NOT NULL,
    "event_date" DATE NOT NULL,
    "region_id" BIGINT NOT NULL
);
ALTER TABLE "Events" ADD PRIMARY KEY("id");


CREATE TABLE "EventsPictures"(
    "id" BIGSERIAL NOT NULL,
    "event_id" BIGINT NOT NULL,
    "picture_url" TEXT NOT NULL
);
ALTER TABLE "EventsPictures" ADD PRIMARY KEY("id");


ALTER TABLE "Authentication" ADD CONSTRAINT "authentication_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("id");

ALTER TABLE "FamilyMembers" ADD CONSTRAINT "familymembers_father_id_foreign" FOREIGN KEY("father_id") REFERENCES "FamilyMembers"("id");

ALTER TABLE "FamilyTrees" ADD CONSTRAINT "familytrees_region_id_foreign" FOREIGN KEY("region_id") REFERENCES "Regions"("id");

ALTER TABLE "AcceptanceTerms" ADD CONSTRAINT "acceptanceterms_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("id");

ALTER TABLE "Accesses" ADD CONSTRAINT "accesses_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("id");

ALTER TABLE "FamilyMembers" ADD CONSTRAINT "familymembers_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("id");

ALTER TABLE "logs" ADD CONSTRAINT "logs_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("id");

ALTER TABLE "Users" ADD CONSTRAINT "users_adress_id_foreign" FOREIGN KEY("adress_id") REFERENCES "Addresses"("id");

ALTER TABLE "Person" ADD CONSTRAINT "person_region_id_foreign" FOREIGN KEY("region_id") REFERENCES "Regions"("id");

ALTER TABLE "FamilyMembers" ADD CONSTRAINT "familymembers_tree_id_foreign" FOREIGN KEY("tree_id") REFERENCES "FamilyTrees"("id");

ALTER TABLE "Person" ADD CONSTRAINT "person_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "Users"("id");

ALTER TABLE "Users" ADD CONSTRAINT "users_role_id_foreign" FOREIGN KEY("role_id") REFERENCES "Roles"("id");

ALTER TABLE "BibliographyPictures" ADD CONSTRAINT "bibliographypictures_person_id_foreign" FOREIGN KEY("person_id") REFERENCES "Person"("id");

ALTER TABLE "FamilyMembers" ADD CONSTRAINT "familymembers_mother_id_foreign" FOREIGN KEY("mother_id") REFERENCES "FamilyMembers"("id");

ALTER TABLE "Users" ADD CONSTRAINT "users_contact_id_foreign" FOREIGN KEY("contact_id") REFERENCES "Contacts"("id");

ALTER TABLE "FamilyTrees" ADD CONSTRAINT "familytrees_
created_by_foreign" FOREIGN KEY("
created_by") REFERENCES "Users"("id");

ALTER TABLE "FamilyMembers" ADD CONSTRAINT "familymembers_picture_id_foreign" FOREIGN KEY("picture_id") REFERENCES "FamilyTreePictures"("id");

ALTER TABLE "Events" ADD CONSTRAINT "events_region_id_foreign" FOREIGN KEY("region_id") REFERENCES "Regions"("id");

ALTER TABLE "EventsPictures" ADD CONSTRAINT "eventspictures_event_id_foreign" FOREIGN KEY("event_id") REFERENCES "Events"("id");


