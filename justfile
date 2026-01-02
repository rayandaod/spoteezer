mod backend

run:
    just backend run

test test_folder="tests":
    just backend test {{test_folder}}

lint:
    just backend lint

type:
    just backend type
