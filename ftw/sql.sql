BEGIN;
CREATE TABLE "router_ulice" (
    "id" serial NOT NULL PRIMARY KEY,
    "nazwa" varchar(250) NOT NULL
)
;
CREATE TABLE "router_linie" (
    "id" serial NOT NULL PRIMARY KEY,
    "kod" varchar(20) NOT NULL,
    "nazwa_linii" varchar(200) NOT NULL,
    "przystanek_poczatkowy_id" integer NOT NULL,
    "przystanek_koncowy_id" integer NOT NULL,
    "trasa_id" integer NOT NULL
)
;
CREATE TABLE "router_przystanki" (
    "id" serial NOT NULL PRIMARY KEY,
    "ulica_id" integer NOT NULL REFERENCES "router_ulice" ("id") DEFERRABLE INITIALLY DEFERRED,
    "lat" numeric(10, 8) NOT NULL,
    "lng" numeric(10, 8) NOT NULL,
    "nazwa_pomocnicza" varchar(100) NOT NULL
)
;
ALTER TABLE "router_linie" ADD CONSTRAINT "przystanek_poczatkowy_id_refs_id_6909f1c0" FOREIGN KEY ("przystanek_poczatkowy_id") REFERENCES "router_przystanki" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "router_linie" ADD CONSTRAINT "przystanek_koncowy_id_refs_id_6909f1c0" FOREIGN KEY ("przystanek_koncowy_id") REFERENCES "router_przystanki" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "router_przystanekpozycja" (
    "id" serial NOT NULL PRIMARY KEY,
    "trasa_id" integer NOT NULL,
    "przystanek_id" integer NOT NULL REFERENCES "router_przystanki" ("id") DEFERRABLE INITIALLY DEFERRED,
    "pozycja" integer NOT NULL,
    "czas_dojazdu" integer NOT NULL
)
;
CREATE TABLE "router_trasy" (
    "id" serial NOT NULL PRIMARY KEY,
    "dlugosc_trasy" integer NOT NULL
)
;
ALTER TABLE "router_linie" ADD CONSTRAINT "trasa_id_refs_id_439b9ae5" FOREIGN KEY ("trasa_id") REFERENCES "router_trasy" ("id") DEFERRABLE INITIALLY DEFERRED;
ALTER TABLE "router_przystanekpozycja" ADD CONSTRAINT "trasa_id_refs_id_17a0ab31" FOREIGN KEY ("trasa_id") REFERENCES "router_trasy" ("id") DEFERRABLE INITIALLY DEFERRED;
CREATE TABLE "router_rozkladprzystanek" (
    "id" serial NOT NULL PRIMARY KEY,
    "linia_id" integer NOT NULL REFERENCES "router_linie" ("id") DEFERRABLE INITIALLY DEFERRED,
    "przystanek_id" integer NOT NULL REFERENCES "router_przystanki" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "router_rozklad" (
    "id" serial NOT NULL PRIMARY KEY,
    "godzina" varchar(2) NOT NULL,
    "minuta" varchar(2) NOT NULL,
    "dzien_powszedni" boolean NOT NULL,
    "niedziela" boolean NOT NULL,
    "nocny" boolean NOT NULL,
    "rozklad_id" integer NOT NULL REFERENCES "router_rozkladprzystanek" ("id") DEFERRABLE INITIALLY DEFERRED
)
;
CREATE TABLE "router_przystanki_linia" (
    "id" serial NOT NULL PRIMARY KEY,
    "przystanki_id" integer NOT NULL REFERENCES "router_przystanki" ("id") DEFERRABLE INITIALLY DEFERRED,
    "linie_id" integer NOT NULL REFERENCES "router_linie" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("przystanki_id", "linie_id")
)
;
CREATE TABLE "router_trasy_przystanki" (
    "id" serial NOT NULL PRIMARY KEY,
    "trasy_id" integer NOT NULL REFERENCES "router_trasy" ("id") DEFERRABLE INITIALLY DEFERRED,
    "przystanekpozycja_id" integer NOT NULL REFERENCES "router_przystanekpozycja" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("trasy_id", "przystanekpozycja_id")
)
;
CREATE TABLE "router_rozkladprzystanek_rozklad" (
    "id" serial NOT NULL PRIMARY KEY,
    "rozkladprzystanek_id" integer NOT NULL REFERENCES "router_rozkladprzystanek" ("id") DEFERRABLE INITIALLY DEFERRED,
    "rozklad_id" integer NOT NULL REFERENCES "router_rozklad" ("id") DEFERRABLE INITIALLY DEFERRED,
    UNIQUE ("rozkladprzystanek_id", "rozklad_id")
)
;
CREATE INDEX "router_linie_przystanek_poczatkowy_id" ON "router_linie" ("przystanek_poczatkowy_id");
CREATE INDEX "router_linie_przystanek_koncowy_id" ON "router_linie" ("przystanek_koncowy_id");
CREATE INDEX "router_linie_trasa_id" ON "router_linie" ("trasa_id");
CREATE INDEX "router_przystanki_ulica_id" ON "router_przystanki" ("ulica_id");
CREATE INDEX "router_przystanekpozycja_trasa_id" ON "router_przystanekpozycja" ("trasa_id");
CREATE INDEX "router_przystanekpozycja_przystanek_id" ON "router_przystanekpozycja" ("przystanek_id");
CREATE INDEX "router_rozkladprzystanek_linia_id" ON "router_rozkladprzystanek" ("linia_id");
CREATE INDEX "router_rozkladprzystanek_przystanek_id" ON "router_rozkladprzystanek" ("przystanek_id");
CREATE INDEX "router_rozklad_rozklad_id" ON "router_rozklad" ("rozklad_id");
COMMIT;
