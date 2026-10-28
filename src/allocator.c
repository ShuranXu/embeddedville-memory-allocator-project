#include "ev_allocator.h"

/*
 * Project surface. Follow the hosted stages in order: contract, boundary tags,
 * explicit free list, allocation/splitting, free/coalescing, then validation.
 * Keep these functions warning-clean while replacing each TODO.
 */
bool ev_allocator_init(ev_allocator_t *allocator, void *arena, size_t arena_size) {
    (void)allocator; (void)arena; (void)arena_size;
    /* TODO(stage-3): validate and initialize one maximal free block. */
    return false;
}

ev_alloc_result_t ev_allocator_alloc(ev_allocator_t *allocator, size_t requested_size) {
    (void)allocator;
    /* TODO(stage-4): checked alignment, first fit, exact fit, and splitting. */
    return (ev_alloc_result_t){.pointer = NULL, .status = requested_size ? EV_ALLOC_EXHAUSTED : EV_ALLOC_ZERO_SIZE, .usable_size = 0};
}

ev_free_status_t ev_allocator_free(ev_allocator_t *allocator, void *pointer) {
    (void)allocator;
    /* TODO(stage-5): classify pointers, release, and immediately coalesce. */
    return pointer == NULL ? EV_FREE_NULL : EV_FREE_INVALID;
}

bool ev_allocator_validate(const ev_allocator_t *allocator, ev_allocator_report_t *report) {
    (void)allocator;
    if (report) *report = (ev_allocator_report_t){0};
    /* TODO(stage-5): walk the arena and list, detect cycles, and account bytes. */
    return false;
}

ev_allocator_stats_t ev_allocator_stats(const ev_allocator_t *allocator) {
    return allocator ? allocator->stats : (ev_allocator_stats_t){0};
}

