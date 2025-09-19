# FIM Examples

This directory contains example files and directories for testing the File Integrity Monitor.

## Structure

```
examples/
└── watchdir/           # Sample directory to monitor
    ├── sample.txt      # Sample text file
    ├── config.ini      # Configuration file
    ├── data.json       # JSON data file
    └── subdir/         # Subdirectory
        └── nested_file.txt  # Nested file
```

## Usage

1. **Initialize baseline:**
   ```bash
   fim init --path examples/watchdir --baseline baseline.json
   ```

2. **Start monitoring:**
   ```bash
   fim watch --path examples/watchdir --baseline baseline.json --events events.json
   ```

3. **Make changes to files:**
   - Edit `sample.txt`
   - Modify `config.ini`
   - Delete `data.json`
   - Add new files
   - Rename files

4. **Stop monitoring** with `Ctrl+C`

5. **Generate report:**
   ```bash
   fim report --events events.json --out report.html
   ```

6. **Verify integrity:**
   ```bash
   fim verify --path examples/watchdir --baseline baseline.json
   ```

## Test Scenarios

### Scenario 1: Basic File Modifications
1. Start monitoring
2. Edit `sample.txt` - add some text
3. Modify `config.ini` - change a setting
4. Stop monitoring
5. Check the generated report

### Scenario 2: File Operations
1. Start monitoring
2. Delete `data.json`
3. Create a new file `new_file.txt`
4. Rename `nested_file.txt` to `renamed_file.txt`
5. Stop monitoring
6. Review events and report

### Scenario 3: Bulk Changes
1. Start monitoring
2. Copy several files into the directory
3. Modify multiple files simultaneously
4. Move files between subdirectories
5. Stop monitoring
6. Analyze the comprehensive report

### Scenario 4: Integrity Verification
1. Create baseline when files are in known good state
2. Make unauthorized changes to files
3. Run verification to detect integrity violations
4. Restore files from backup
5. Verify integrity is restored

## Expected Results

After running the test scenarios, you should see:

- **Baseline files** with SHA256 hashes of all monitored files
- **Event logs** showing all detected changes with timestamps
- **HTML reports** with visual charts and detailed tables
- **Verification results** showing any integrity violations

The HTML report will include:
- Summary cards showing counts of added/modified/deleted files
- Interactive bar chart showing event distribution
- Detailed table with all events, hashes, and timestamps
- Professional styling with responsive design
