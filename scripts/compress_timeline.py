import os
import sys
import datetime
import re

def compress_timeline(timeline_path):
    if not os.path.exists(timeline_path):
        print(f"Error: {timeline_path} does not exist.")
        return

    archive_dir = os.path.join(os.path.dirname(timeline_path), 'timeline_archive')
    os.makedirs(archive_dir, exist_ok=True)

    with open(timeline_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines(keepends=True)

    # Timeline uses markdown table format: | When | Event | Arc | Chapter |
    # We count data rows (lines starting with | that are NOT header or separator rows)
    header_pattern = re.compile(r'^\|\s*(When|#|---)')
    event_rows = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('|'):
            continue
        if header_pattern.match(stripped):
            continue
        parts = stripped.split('|')
        if len(parts) > 2 and '---' in parts[1]:
            continue
        event_rows.append(line)

    if len(event_rows) > 20:
        old_events = event_rows[:-20]
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        archive_path = os.path.join(archive_dir, f"archive_{timestamp}.md")
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write("# Timeline Archive\n\n")
            f.write("| When | Event | Arc | Chapter |\n")
            f.write("|------|-------|-----|---------|\n")
            f.writelines(old_events)

        # Rebuild timeline.md: keep header + separator + last 20 events
        new_lines = []
        in_table = False
        header_written = False
        for line in lines:
            if line.strip().startswith('|') and not header_written:
                # Write header rows (first two | lines: header + separator)
                new_lines.append(line)
                if '---' in line:
                    header_written = True
                    in_table = True
                continue
            if in_table and line.strip().startswith('|'):
                continue  # Skip all old data rows
            new_lines.append(line)

        # Append note + recent events
        with open(timeline_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            f.write(f"\n> **注**：过往 {len(old_events)} 条早期时间线已被压缩至 timeline_archive/\n\n")
            f.writelines(event_rows[-20:])

        print(f"Timeline Compression complete: Archived {len(old_events)} old events to {os.path.basename(archive_path)}")
    else:
        print(f"Timeline Check: Currently {len(event_rows)} events. No compression needed yet (<20).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compress_timeline.py <path_to_timeline.md>")
        sys.exit(1)
    compress_timeline(sys.argv[1])
