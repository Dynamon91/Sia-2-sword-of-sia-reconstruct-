PREFIX ?= arm-none-eabi-
CC = $(PREFIX)gcc
CFLAGS = -mcpu=arm7tdmi -mthumb -mthumb-interwork -O2 -ffreestanding -fno-builtin -Wall -Wextra
all: build/sia2_lab.gba
build:
	mkdir -p build
build/start.o: src/start.s | build
	$(CC) -mcpu=arm7tdmi -marm -c $< -o $@
build/game.o: src/game.c src/game.h src/alignment.h | build
	$(CC) $(CFLAGS) -c $< -o $@
build/main.o: src/main.c src/settings.h src/game.h src/alignment.h src/story.h assets/assets.h assets/room.h assets/ui.h | build
	$(CC) $(CFLAGS) -c $< -o $@
build/story.o: src/story.c src/story.h assets/assets.h | build
	$(CC) $(CFLAGS) -c $< -o $@
build/assets.o: src/assets.s assets/visuals.bin assets/audio_title.pcm assets/audio_intro.pcm assets/audio_level.pcm assets/font.bin assets/room.bin assets/room_sprites.bin assets/room_sky.bin assets/bridge.bin assets/bridge_sky.bin assets/bridge_run.bin assets/ui_palette.bin assets/ui_tiles.bin assets/ui_dialogs.bin assets/room_backdrop.bin assets/room_spans.bin assets/bridge_backdrop.bin assets/bridge_spans.bin | build
	$(CC) -mcpu=arm7tdmi -marm -c $< -o $@
build/sia2_lab.elf: build/start.o build/game.o build/main.o build/story.o build/assets.o link.ld
	$(CC) -mcpu=arm7tdmi -mthumb-interwork -nostdlib -T link.ld -Wl,-Map,build/sia2_lab.map build/start.o build/game.o build/main.o build/story.o build/assets.o -lgcc -o $@
build/sia2_lab.gba: build/sia2_lab.elf tools/fix_header.py
	$(PREFIX)objcopy -O binary $< $@
	python3 tools/fix_header.py $@
test: | build
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g src/game.c tests/test_game.c -o build/test_game
	./build/test_game
	gcc -std=c99 -Wall -Wextra -Werror -fsanitize=undefined,address -g tests/test_settings.c -o build/test_settings
	./build/test_settings
clean:
	rm -rf build
.PHONY: all test clean
