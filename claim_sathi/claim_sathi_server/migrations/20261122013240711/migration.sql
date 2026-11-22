BEGIN;

--
-- ACTION CREATE TABLE
--
CREATE TABLE "voice_statement" (
    "id" bigserial PRIMARY KEY,
    "speakerRole" text NOT NULL,
    "language" text NOT NULL,
    "durationSeconds" bigint NOT NULL,
    "transcript" text NOT NULL,
    "extractedKeyFacts" text,
    "confidenceScore" double precision NOT NULL,
    "audioDataBase64" text,
    "timestamp" timestamp without time zone NOT NULL,
    "claimId" text
);


--
-- MIGRATION VERSION FOR claim_sathi
--
INSERT INTO "serverpod_migrations" ("module", "version", "timestamp")
    VALUES ('claim_sathi', '20261122013240711', now())
    ON CONFLICT ("module")
    DO UPDATE SET "version" = '20261122013240711', "timestamp" = now();

--
-- MIGRATION VERSION FOR serverpod
--
INSERT INTO "serverpod_migrations" ("module", "version", "timestamp")
    VALUES ('serverpod', '20260824182259319', now())
    ON CONFLICT ("module")
    DO UPDATE SET "version" = '20260824182259319', "timestamp" = now();

--
-- MIGRATION VERSION FOR serverpod_auth_idp
--
INSERT INTO "serverpod_migrations" ("module", "version", "timestamp")
    VALUES ('serverpod_auth_idp', '20261015164015382', now())
    ON CONFLICT ("module")
    DO UPDATE SET "version" = '20261015164015382', "timestamp" = now();

--
-- MIGRATION VERSION FOR serverpod_auth_core
--
INSERT INTO "serverpod_migrations" ("module", "version", "timestamp")
    VALUES ('serverpod_auth_core', '20260924105232991', now())
    ON CONFLICT ("module")
    DO UPDATE SET "version" = '20260924105232991', "timestamp" = now();


COMMIT;
