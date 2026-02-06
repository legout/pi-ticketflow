# Implementation: pt-zwns

## Summary
Added comprehensive pytest coverage for priority reclassify classifier rules and apply-mode frontmatter patching.

## Files Changed
- `tests/test_priority_reclassify.py` - Added 35 new tests across 3 test classes

## Test Coverage Added

### TestRubricMappingComprehensive (20 tests)
Comprehensive coverage of the P0-P4 rubric keyword mappings:
- **P0 (critical-risk)**: security, data-loss, system outage, compliance keywords
- **P1 (high-impact)**: user impact, release blocker, performance, correctness keywords
- **P2 (product-feature)**: standard work, integration/API keywords
- **P3 (engineering-quality)**: quality, DX, observability, testing keywords
- **P4 (maintenance-polish)**: polish, docs, types keywords
- **TAG_MAP coverage**: All 21 tag mappings tested
- **TYPE_DEFAULTS coverage**: All 6 type defaults tested
- **Precedence rules**: Tags take precedence over description keywords
- **Ambiguous handling**: Unknown priority returned when no clear match

### TestFrontmatterPreservation (10 tests)
Tests that apply-mode patching preserves unrelated frontmatter fields:
- `parse_frontmatter()` - Parses frontmatter correctly, handles missing frontmatter
- `update_frontmatter_priority()` - Updates only priority field, preserves others
- `update_frontmatter_priority()` - Preserves indentation
- `update_frontmatter_priority()` - Adds priority if missing
- `add_note_to_ticket_body()` - Creates Notes section if missing
- `add_note_to_ticket_body()` - Appends to existing Notes section
- `update_ticket_priority()` - Integration test preserving all custom fields (custom_field, assignee, due_date)
- `update_ticket_priority()` - Works without existing Notes section
- `update_ticket_priority()` - Handles missing ticket file gracefully

### TestTempTicketsIntegration (5 tests)
Integration-style tests with temporary `.tickets/` directory:
- **Full workflow test**: Multiple tickets with different tags, verifies classification
- **Apply mode test**: Real file updates with priority change and audit note
- **Determinism test**: Classifier produces consistent results across multiple runs
- **Tag precedence test**: Highest priority tag wins when multiple tags present

## Test Statistics
- Total tests in file: 71 (up from 36)
- New tests added: 35
- All tests pass: ✓

## Verification
```bash
cd /home/volker/coding/pi-ticketflow
source .venv/bin/activate
python -m pytest tests/test_priority_reclassify.py -v
# 71 passed

python -m pytest tests/ -v
# 399 passed
```

## Acceptance Criteria
- [x] Unit tests for rubric mapping + keyword rules
- [x] Tests that patching preserves unrelated frontmatter fields
- [x] Integration-style test with a temporary `.tickets/` directory
- [x] Tests must not modify real repo tickets (all use tmp_path)
