BEGIN;
ALTER TABLE router_przystanki ADD COLUMN "kod" VARCHAR(20);
UPDATE router_przystanki SET kod = 0;
ALTER TABLE router_przystanki ALTER COLUMN kod SET NOT NULL;
COMMIT;