DOCKER:
        docker build -t nsql:sem .
        docker-compose up --build

        (ps: nekdy pripojeni na volume trochu dele trva, reload vzdy pomuze...)

Pristupove udaje uzivatelu:
    nicknames: Duck, Mallard, NinjaDuck, Shoveler, Psyduck
    passw: quack

overeni cachovani pres redis - redis comander:
    localhost:8081
    user: root
    passw: qwerty

pristup do databaze (volitelne) - mongodbcompass:
    admin:admin