Choosing the Result Backend
===================

Celery needs to store or send the states somewhere to keep track of the tasks’ states.

There are several choices available, including:

Redis
-----

Redis is an open source, BSD licensed, advanced key-value data store with optional durability.

You can either download the latest Redis tar ball from the redis.io web site, or you can alternatively use this special URL that always points to the latest stable Redis version, that is, http://download.redis.io/redis-stable.tar.gz.

In order to compile Redis follow this simple steps:

wget http://download.redis.io/redis-stable.tar.gz
tar xvzf redis-stable.tar.gz
cd redis-stable
make

At this point you can try if your build works correctly typing make test, but this is an optional step. After the compilation the src directory inside the Redis distribution is populated with the different executables that are part of Redis:

    redis-server is the Redis Server itself.
    redis-cli is the command line interface utility to talk with Redis.
    redis-benchmark is used to check Redis performances.
    redis-check-aof and redis-check-dump are useful in the rare event of corrupted data files.

