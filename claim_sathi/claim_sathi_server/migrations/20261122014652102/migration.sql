BEGIN;

--
-- ACTION CREATE TABLE
--
CREATE TABLE "claim_verdict" (
    "id" bigserial PRIMARY KEY,
    "claimNumber" text NOT NULL,
    "policyholderName" text NOT NULL,
    "insurerName" text NOT NULL,
    "claimedAmount" double precision NOT NULL,
    "verdictStatus" text NOT NULL,
    "disputedClause" text NOT NULL,
    "legalBasis" text NOT NULL,
    "spokenDefenseHindi" text NOT NULL,
    "spokenDefenseEnglish" text NOT NULL,
    "grievanceLetterMarkdown" text NOT NULL,
    "evidenceCount" bigint NOT NULL,
    "voiceStatementsCount" bigint NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);


--
-- MIGRATION VERSION FOR claim_sathi
--
INSERT INTO "serverpod_migrations" ("module", "version", "timestamp")
    VALUES ('claim_sathi', '20261122014652102', now())
    ON CONFLICT ("module")
    DO UPDATE SET "version" = '20261122014652102', "timestamp" = now();

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
