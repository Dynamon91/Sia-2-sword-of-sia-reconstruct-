PREFIX ?= arm-none-eabi-
CC = $(PREFIX)gcc
CFLAGS = -mcpu=arm7tdmi -mthumb -mthumb-interwork -O2 -ffreestanding -fno-builtin -Wall -Wextra
.DEFAULT_GOAL := all
# Track every included header, including scenery and transitive asset headers.
DEPFLAGS = -MMD -MP
-include $(wildcard build/*.d)
all: build/sia2_lab.gba
build:
	mkdir -p build
build/start.o: src/start.s | build
	$(CC) -mcpu=arm7tdmi -marm -c $< -o $@
build/game.o: src/game.c src/game.h src/level_progress.h src/alignment.h | build
	$(CC) $(CFLAGS) $(DEPFLAGS) -c $< -o $@
build/main.o: src/main.c src/settings.h src/game.h src/alignment.h src/scenery.h src/story.h assets/assets.h assets/room.h assets/ui.h | build
	$(CC) $(CFLAGS) $(DEPFLAGS) -c $< -o $@
build/level_progress.o: src/level_progress.c src/level_progress.h | build
	$(CC) $(CFLAGS) $(DEPFLAGS) -c $< -o $@
build/story.o: src/story.c src/story.h assets/assets.h | build
	$(CC) $(CFLAGS) $(DEPFLAGS) -c $< -o $@
build/assets.o: src/assets.s assets/jump_cycle.bin assets/ledge_cycle.bin assets/ambient_gems.bin assets/gap.bin assets/guard2_sprite.bin assets/walk_cycle.bin assets/attack_cycle.bin assets/ui_more_tiles.bin assets/guard_room.bin assets/guard_sprite.bin assets/cliff.bin assets/visuals.bin assets/audio_title.pcm assets/audio_level.pcm assets/font.bin assets/room.bin assets/room_sprites.bin assets/room_sky.bin assets/bridge.bin assets/bridge_sky.bin assets/bridge_run.bin assets/ui_palette.bin assets/ui_tiles.bin assets/ui_dialogs.bin assets/room_backdrop.bin assets/room_spans.bin assets/bridge_backdrop.bin assets/bridge_spans.bin | build
	$(CC) -mcpu=arm7tdmi -marm -c $< -o $@
build/assets.o: assets/upper_background.bin assets/ui_digit5_tiles.bin assets/cloud_strip.bin assets/continuation_background.bin assets/bridge_run_background.bin assets/riser_background.bin
build/assets.o: assets/ramp_lower_background.bin assets/ramp_upper_background.bin assets/island_gap_background.bin assets/lever_entry_background.bin assets/lever_room_background.bin
build/sia2_lab.elf: build/start.o build/game.o build/main.o build/story.o build/level_progress.o build/assets.o link.ld
	$(CC) -mcpu=arm7tdmi -mthumb-interwork -nostdlib -T link.ld -Wl,-Map,build/sia2_lab.map build/start.o build/game.o build/main.o build/story.o build/level_progress.o build/assets.o -lgcc -o $@
build/sia2_lab.gba: build/sia2_lab.elf tools/fix_header.py
	$(PREFIX)objcopy -O binary $< $@
	python3 tools/fix_header.py $@
test: | build
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_lever_route.c -o build/test_lever_route
	./build/test_lever_route
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_island_gap.c -o build/test_island_gap
	./build/test_island_gap
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_ramp_route.c -o build/test_ramp_route
	./build/test_ramp_route
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_upper_route.c -o build/test_upper_route
	./build/test_upper_route
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_bridge_run.c -o build/test_bridge_run
	./build/test_bridge_run
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_continuation.c -o build/test_continuation
	./build/test_continuation
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_air_motion.c -o build/test_air_motion
	./build/test_air_motion
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_ledge.c -o build/test_ledge
	./build/test_ledge
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_collisions.c -o build/test_collisions
	./build/test_collisions
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_lives.c -o build/test_lives
	./build/test_lives
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_game.c -o build/test_game
	./build/test_game
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c src/level_progress.c tests/test_gap_motion.c -o build/test_gap_motion
	./build/test_gap_motion
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g tests/test_settings.c -o build/test_settings
	./build/test_settings
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/level_progress.c tests/test_level_progress.c -o build/test_level_progress
	./build/test_level_progress
clean:
	rm -rf build
.PHONY: all test clean
