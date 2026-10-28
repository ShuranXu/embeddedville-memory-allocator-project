CC ?= gcc-13
CFLAGS := -std=c11 -O1 -g -Wall -Wextra -Wpedantic -Werror -Iinclude
SANITIZERS := -fsanitize=address,undefined -fno-omit-frame-pointer
BUILD := build

.PHONY: all test baseline clean
all: $(BUILD)/public-tests $(BUILD)/baseline

$(BUILD):
	mkdir -p $@

$(BUILD)/public-tests: src/allocator.c tests/public/test_allocator.c include/ev_allocator.h | $(BUILD)
	$(CC) $(CFLAGS) $(SANITIZERS) src/allocator.c tests/public/test_allocator.c -o $@

$(BUILD)/baseline: src/bump_baseline.c tools/baseline.c | $(BUILD)
	$(CC) $(CFLAGS) src/bump_baseline.c tools/baseline.c -o $@

test: $(BUILD)/public-tests
	./$(BUILD)/public-tests

baseline: $(BUILD)/baseline
	./$(BUILD)/baseline

clean:
	rm -rf $(BUILD)

