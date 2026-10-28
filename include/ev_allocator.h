#ifndef EV_ALLOCATOR_H
#define EV_ALLOCATOR_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

typedef enum {
    EV_ALLOC_OK = 0,
    EV_ALLOC_ZERO_SIZE,
    EV_ALLOC_OVERFLOW,
    EV_ALLOC_EXHAUSTED,
    EV_ALLOC_CORRUPT
} ev_alloc_status_t;

typedef enum {
    EV_FREE_OK = 0,
    EV_FREE_NULL,
    EV_FREE_MISALIGNED,
    EV_FREE_FOREIGN,
    EV_FREE_INVALID,
    EV_FREE_DOUBLE,
    EV_FREE_CORRUPT
} ev_free_status_t;

typedef struct { void *pointer; ev_alloc_status_t status; size_t usable_size; } ev_alloc_result_t;
typedef struct {
    size_t arena_size, payload_bytes, free_bytes, largest_free_block;
    size_t active_allocations, allocation_failures, total_search_probes;
    size_t maximum_search_probes, split_count, coalesce_count;
} ev_allocator_stats_t;
typedef struct { bool valid; size_t block_count, free_block_count, accounted_bytes; uint32_t error_mask; } ev_allocator_report_t;
typedef struct { unsigned char *arena; size_t arena_size; void *free_head; ev_allocator_stats_t stats; uint64_t cookie; } ev_allocator_t;

bool ev_allocator_init(ev_allocator_t *allocator, void *arena, size_t arena_size);
ev_alloc_result_t ev_allocator_alloc(ev_allocator_t *allocator, size_t requested_size);
ev_free_status_t ev_allocator_free(ev_allocator_t *allocator, void *pointer);
bool ev_allocator_validate(const ev_allocator_t *allocator, ev_allocator_report_t *report);
ev_allocator_stats_t ev_allocator_stats(const ev_allocator_t *allocator);

#endif

