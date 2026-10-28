#include <stddef.h>
#include <stdint.h>

typedef struct { unsigned char *arena; size_t capacity; size_t cursor; } ev_bump_t;
void ev_bump_init(ev_bump_t *b, void *arena, size_t capacity) { b->arena = arena; b->capacity = capacity; b->cursor = 0; }
void *ev_bump_alloc(ev_bump_t *b, size_t size) {
    if (size == 0 || size > SIZE_MAX - 15) return NULL;
    size = (size + 15u) & ~(size_t)15u;
    if (size > b->capacity - b->cursor) return NULL;
    void *result = b->arena + b->cursor; b->cursor += size; return result;
}

