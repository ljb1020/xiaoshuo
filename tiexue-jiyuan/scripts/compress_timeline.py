import os
import sys
import datetime

def compress_timeline(timeline_path):
    if not os.path.exists(timeline_path):
        print(f"Error: {timeline_path} does not exist.")
        return

    archive_dir = os.path.join(os.path.dirname(timeline_path), 'timeline_archive')
    os.makedirs(archive_dir, exist_ok=True)
    
    with open(timeline_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # We look for markdown list items which count as events
    events = [line for line in lines if line.strip().startswith("- ")]
    
    # Compress if we have more than 20 recorded chronological events
    if len(events) > 20:
        old_events = events[:-20]
        recent_events = events[-20:]
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
        archive_path = os.path.join(archive_dir, f"archive_{timestamp}.md")
        with open(archive_path, 'w', encoding='utf-8') as f:
            f.write("# Timeline Archive\n\n")
            f.writelines(old_events)
            
        # Rebuild timeline.md
        header = []
        for line in lines:
            if line.strip().startswith("- "):
                break
            header.append(line)
            
        with open(timeline_path, 'w', encoding='utf-8') as f:
            f.writelines(header)
            f.write(f"\n> **注**：过往 {len(old_events)} 条早期时间线已被压缩至 timeline_archive/\n\n")
            f.writelines(recent_events)
            
        print(f"Timeline Compression complete: Archived {len(old_events)} old events to {os.path.basename(archive_path)}")
    else:
        print(f"Timeline Check: Currently {len(events)} events. No compression needed yet (<20).")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compress_timeline.py <path_to_timeline.md>")
        sys.exit(1)
    compress_timeline(sys.argv[1])
