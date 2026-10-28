#include "ev_allocator.h"
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static _Alignas(16) unsigned char arena[64u * 1024u];
int main(void) {
    ev_allocator_t allocator;
    assert(ev_allocator_init(&allocator, arena, sizeof arena));
    assert(ev_allocator_alloc(&allocator, 0).status == EV_ALLOC_ZERO_SIZE);
    ev_alloc_result_t a = ev_allocator_alloc(&allocator, 17);
    assert(a.status == EV_ALLOC_OK && a.pointer != NULL);
    assert(((uintptr_t)a.pointer & 15u) == 0u);
    memset(a.pointer, 0xA5, 17);
    assert(ev_allocator_free(&allocator, NULL) == EV_FREE_NULL);
    assert(ev_allocator_free(&allocator, a.pointer) == EV_FREE_OK);
    assert(ev_allocator_free(&allocator, a.pointer) == EV_FREE_DOUBLE);
    ev_allocator_report_t report;
    assert(ev_allocator_validate(&allocator, &report) && report.valid);
    puts("public allocator contract checks passed");
    return 0;
}

