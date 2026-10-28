// SPDX-License-Identifier: GPL-2.0-only
#include <linux/init.h>
#include <linux/module.h>
#include <linux/slab.h>

static size_t sizes[] = {24, 96, 512, 4096, 32768};
static void *objects[ARRAY_SIZE(sizes)];
static int __init ev_probe_init(void) {
    size_t i;
    for (i = 0; i < ARRAY_SIZE(sizes); ++i) {
        objects[i] = kmalloc(sizes[i], GFP_KERNEL);
        pr_info("ev_kmalloc_probe request=%zu object=%px\n", sizes[i], objects[i]);
    }
    return 0;
}
static void __exit ev_probe_exit(void) { size_t i; for (i = 0; i < ARRAY_SIZE(sizes); ++i) kfree(objects[i]); }
module_init(ev_probe_init); module_exit(ev_probe_exit);
MODULE_LICENSE("GPL"); MODULE_DESCRIPTION("EmbeddedVille read-only kmalloc observation helper");

