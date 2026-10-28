#include <stdio.h>
#include <stddef.h>

typedef struct { unsigned char *arena; size_t capacity; size_t cursor; } ev_bump_t;
void ev_bump_init(ev_bump_t *, void *, size_t);
void *ev_bump_alloc(ev_bump_t *, size_t);

int main(void) {
    static unsigned char arena[64u * 1024u]; ev_bump_t bump; size_t accepted = 0;
    ev_bump_init(&bump, arena, sizeof arena);
    for (size_t round = 0; round < 512; ++round) if (ev_bump_alloc(&bump, (round % 7u + 1u) * 48u)) ++accepted;
    printf("{\"allocator\":\"bump-baseline\",\"accepted\":%zu,\"arenaBytes\":%zu,\"reclaims\":0}\n", accepted, sizeof arena);
    return accepted > 0 ? 0 : 1;
}

