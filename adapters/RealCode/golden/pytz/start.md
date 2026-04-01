# pytz - Python Timezone Handling Library

## Project Goal

Build a comprehensive Python timezone handling library that allows developers to perform accurate, cross-platform timezone calculations using the IANA (Olson) timezone database without manually parsing timezone data files, tracking daylight saving time transitions, or writing boilerplate conversion code. The library provides timezone object creation via `timezone()`, naive-datetime localization via `localize()`, cross-timezone conversion via `astimezone()`, timezone normalization via `normalize()`, fixed-offset timezone support via `FixedOffset`, country-to-timezone mapping via `country_timezones`, and lazily-loaded collection classes (`LazyList`, `LazySet`, `LazyDict`) for efficient internal data management. All timezone objects follow a singleton/caching pattern, support pickle serialization, and handle edge cases such as ambiguous times, non-existent times, and historical timezone changes.

---

## Background and Problem

Without this library, developers are forced to manually parse raw IANA timezone database binary files, implement daylight saving time transition logic from scratch, track historical timezone rule changes across hundreds of regions, and write repetitive boilerplate code for every timezone conversion. This leads to error-prone time calculations, incorrect handling of DST boundaries (causing off-by-one-hour bugs), duplicated effort across projects, and a significant maintenance burden whenever the IANA database is updated.

With this library, developers simply call `pytz.timezone('US/Eastern')` to obtain a fully functional timezone object, use `.localize()` to attach timezone information to naive datetime objects (with correct DST inference), use `.astimezone()` for seamless cross-timezone conversion, and rely on well-defined exception types (`AmbiguousTimeError`, `NonExistentTimeError`, `UnknownTimeZoneError`) to handle edge cases gracefully. The library ships with the IANA database pre-compiled, caches timezone objects as singletons for performance, and provides lazily-loaded collections so that startup cost is negligible.

---

## Core Features

### Feature 1: Timezone Object Creation and Caching

**As a developer**, I want to create timezone objects by name (e.g., `'US/Eastern'`, `'Asia/Shanghai'`, `'UTC'`) and have them cached as singletons, so I can efficiently reuse timezone objects without redundant parsing or memory overhead.

**Expected Behavior / Usage:**

*1.1 Creating timezone objects via `timezone()` -- Core entry point*

Calling `pytz.timezone(zone_name)` returns a timezone object that inherits from `datetime.tzinfo`. The `zone_name` parameter is a string matching an IANA timezone identifier. The returned object has a `.zone` attribute reflecting the canonical timezone name. If the name is `'UTC'`, the returned object is the same singleton as `pytz.utc`.

*1.2 Singleton caching -- Same name yields identical object*

Repeated calls to `timezone()` with the same zone name return the exact same object (i.e., `timezone('US/Eastern') is timezone('US/Eastern')` evaluates to `True`). This applies to all timezone types including DST-aware, static, and UTC.

*1.3 Case-insensitive name resolution -- Flexible lookup*

The `timezone()` function performs case-insensitive matching, so `timezone('us/eastern')` returns the same object as `timezone('US/Eastern')`. The `.zone` attribute always reflects the canonical casing.

*1.4 Unknown timezone error -- Clear error reporting*

If an unrecognized timezone name is passed, `timezone()` raises `pytz.UnknownTimeZoneError` (a subclass of `KeyError`).

**Test Cases:** `tests/test_cases/feature1_timezone_creation.json`

```json
{
    "description": "Test timezone object creation, singleton caching, case-insensitive resolution, and error handling for unknown timezones.",
    "cases": [
        {
            "input": {"action": "create", "zone": "US/Eastern"},
            "expected_output": {"zone": "US/Eastern", "type": "DstTzInfo"}
        },
        {
            "input": {"action": "create", "zone": "UTC"},
            "expected_output": {"zone": "UTC", "type": "UTC", "is_pytz_utc": true}
        },
        {
            "input": {"action": "create", "zone": "Asia/Shanghai"},
            "expected_output": {"zone": "Asia/Shanghai", "type": "DstTzInfo"}
        },
        {
            "input": {"action": "singleton_check", "zone": "US/Eastern"},
            "expected_output": {"same_object": true}
        },
        {
            "input": {"action": "singleton_check", "zone": "UTC"},
            "expected_output": {"same_object": true}
        },
        {
            "input": {"action": "case_insensitive", "zone": "us/eastern", "canonical": "US/Eastern"},
            "expected_output": {"same_object": true, "zone": "US/Eastern"}
        },
        {
            "input": {"action": "create", "zone": "GMT"},
            "expected_output": {"zone": "GMT", "type": "StaticTzInfo"}
        },
        {
            "input": {"action": "create", "zone": "Unknown/Timezone"},
            "expected_output": {"error": "UnknownTimeZoneError"}
        },
        {
            "input": {"action": "create", "zone": ""},
            "expected_output": {"error": "UnknownTimeZoneError"}
        }
    ]
}
```

---

### Feature 2: Lazy Collection Classes

**As a developer**, I want to use lazily-loaded collection classes (`LazyList`, `LazySet`, `LazyDict`) that defer computation until first access, so I can minimize startup time and memory usage when importing pytz.

**Expected Behavior / Usage:**

*2.1 LazyList -- Deferred list computation*

`LazyList` accepts a fill function that populates the list on first access. Before any element is accessed, the fill function has not been called. Once any list operation (indexing, iteration, `len()`, etc.) is performed, the fill function runs exactly once and the `LazyList` behaves identically to a regular Python `list`.

*2.2 LazySet -- Deferred set computation*

`LazySet` works similarly to `LazyList` but produces a `set`. It supports standard set operations (`in`, `len()`, iteration, `union`, `intersection`, etc.) and triggers its fill function on first use.

*2.3 LazyDict -- Deferred dictionary computation*

`LazyDict` produces a `dict` on demand. It supports standard dict operations (`[]`, `.get()`, `.keys()`, `.values()`, `.items()`, `in`, `len()`) and triggers its fill function on first use.

**Test Cases:** `tests/test_cases/feature2_lazy_collections.json`

```json
{
    "description": "Test LazyList, LazySet, and LazyDict deferred computation, correct behavior after materialization, and standard collection operations.",
    "cases": [
        {
            "input": {"class": "LazyList", "fill_data": [1, 2, 3], "operation": "len"},
            "expected_output": 3
        },
        {
            "input": {"class": "LazyList", "fill_data": [10, 20, 30], "operation": "getitem", "index": 1},
            "expected_output": 20
        },
        {
            "input": {"class": "LazyList", "fill_data": [1, 2, 3], "operation": "contains", "value": 2},
            "expected_output": true
        },
        {
            "input": {"class": "LazyList", "fill_data": [1, 2, 3], "operation": "list"},
            "expected_output": [1, 2, 3]
        },
        {
            "input": {"class": "LazySet", "fill_data": ["a", "b", "c"], "operation": "len"},
            "expected_output": 3
        },
        {
            "input": {"class": "LazySet", "fill_data": ["a", "b", "c"], "operation": "contains", "value": "b"},
            "expected_output": true
        },
        {
            "input": {"class": "LazySet", "fill_data": ["a", "b", "c"], "operation": "contains", "value": "z"},
            "expected_output": false
        },
        {
            "input": {"class": "LazyDict", "fill_data": {"x": 1, "y": 2}, "operation": "getitem", "key": "x"},
            "expected_output": 1
        },
        {
            "input": {"class": "LazyDict", "fill_data": {"x": 1, "y": 2}, "operation": "keys"},
            "expected_output": ["x", "y"]
        },
        {
            "input": {"class": "LazyDict", "fill_data": {"x": 1, "y": 2}, "operation": "len"},
            "expected_output": 2
        }
    ]
}
```

---

### Feature 3: Time Localization

**As a developer**, I want to convert a naive `datetime` object into a timezone-aware `datetime` using `localize()`, so I can attach correct timezone information (including DST status) without manually computing offsets.

**Expected Behavior / Usage:**

*3.1 Basic localization -- Attaching timezone to a naive datetime*

Calling `tz.localize(naive_dt)` returns a new `datetime` with `.tzinfo` set to the appropriate timezone representation for that wall-clock time. For unambiguous times, the correct offset and abbreviation are automatically determined. The returned datetime's `.strftime('%Z')` and `.strftime('%z')` reflect the resolved timezone.

*3.2 DST-aware localization -- Handling ambiguous times*

During the "fall back" DST transition, the same wall-clock time occurs twice. Calling `tz.localize(dt, is_dst=True)` selects the DST interpretation; `is_dst=False` selects the standard-time interpretation. Passing `is_dst=None` raises `AmbiguousTimeError` when the time is ambiguous.

*3.3 Non-existent time detection -- Handling "spring forward" gaps*

During the "spring forward" DST transition, certain wall-clock times do not exist. Calling `tz.localize(dt, is_dst=None)` raises `NonExistentTimeError`. Passing `is_dst=True` or `is_dst=False` resolves the time to the nearest valid interpretation.

**Test Cases:** `tests/test_cases/feature3_1_basic_localization.json`

```json
{
    "description": "Test basic localization of naive datetime objects to timezone-aware datetimes in various timezones.",
    "cases": [
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 06:00:00"},
            "expected_output": "2002-10-27 06:00:00 EST (-0500)"
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-07-07 06:00:00"},
            "expected_output": "2002-07-07 06:00:00 EDT (-0400)"
        },
        {
            "input": {"zone": "Europe/Amsterdam", "datetime": "2002-10-27 06:00:00"},
            "expected_output": "2002-10-27 06:00:00 CET (+0100)"
        },
        {
            "input": {"zone": "Asia/Shanghai", "datetime": "2002-10-27 06:00:00"},
            "expected_output": "2002-10-27 06:00:00 CST (+0800)"
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2023-01-15 10:30:00"},
            "expected_output": "2023-01-15 10:30:00 EST (-0500)"
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2023-06-15 10:30:00"},
            "expected_output": "2023-06-15 10:30:00 EDT (-0400)"
        }
    ]
}
```

**Test Cases:** `tests/test_cases/feature3_2_ambiguous_time.json`

```json
{
    "description": "Test handling of ambiguous times during DST fall-back transitions using is_dst parameter.",
    "cases": [
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 01:30:00", "is_dst": false},
            "expected_output": "2002-10-27 01:30:00 EST (-0500)"
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 01:30:00", "is_dst": true},
            "expected_output": "2002-10-27 01:30:00 EDT (-0400)"
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 01:30:00", "is_dst": null},
            "expected_output": {"error": "AmbiguousTimeError"}
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 01:00:00", "is_dst": false},
            "expected_output": "2002-10-27 01:00:00 EST (-0500)"
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 01:00:00", "is_dst": true},
            "expected_output": "2002-10-27 01:00:00 EDT (-0400)"
        }
    ]
}
```

**Test Cases:** `tests/test_cases/feature3_3_nonexistent_time.json`

```json
{
    "description": "Test handling of non-existent times during DST spring-forward transitions.",
    "cases": [
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-04-07 02:30:00", "is_dst": null},
            "expected_output": {"error": "NonExistentTimeError"}
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-04-07 02:00:00", "is_dst": null},
            "expected_output": {"error": "NonExistentTimeError"}
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-04-07 02:30:00", "is_dst": true},
            "expected_output": "2002-04-07 02:30:00 EDT (-0400)"
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-04-07 02:30:00", "is_dst": false},
            "expected_output": "2002-04-07 02:30:00 EST (-0500)"
        }
    ]
}
```

---

### Feature 4: Timezone Normalization

**As a developer**, I want to normalize a timezone-aware `datetime` after arithmetic operations using `normalize()`, so I can ensure the timezone abbreviation and offset remain correct when datetime arithmetic crosses a DST boundary.

**Expected Behavior / Usage:**

After performing arithmetic (e.g., adding/subtracting `timedelta`) on a localized `datetime`, the `.tzinfo` may no longer reflect the correct DST state. Calling `tz.normalize(dt)` recalculates the correct timezone offset and abbreviation. If the datetime is already correct, `normalize()` returns an equivalent datetime. Normalization converts the datetime to UTC internally, then back to the target timezone, ensuring consistency.

**Test Cases:** `tests/test_cases/feature4_normalization.json`

```json
{
    "description": "Test timezone normalization after datetime arithmetic crosses DST boundaries.",
    "cases": [
        {
            "input": {
                "zone": "US/Eastern",
                "datetime": "2002-10-27 01:00:00",
                "is_dst": false,
                "delta_minutes": -10
            },
            "expected_output": {
                "before_normalize": "2002-10-27 00:50:00 EST (-0500)",
                "after_normalize": "2002-10-27 01:50:00 EDT (-0400)"
            }
        },
        {
            "input": {
                "zone": "US/Eastern",
                "datetime": "2002-10-27 01:00:00",
                "is_dst": true,
                "delta_minutes": 60
            },
            "expected_output": {
                "before_normalize": "2002-10-27 02:00:00 EDT (-0400)",
                "after_normalize": "2002-10-27 01:00:00 EST (-0500)"
            }
        },
        {
            "input": {
                "zone": "US/Eastern",
                "datetime": "2002-04-07 01:00:00",
                "delta_minutes": 60
            },
            "expected_output": {
                "before_normalize": "2002-04-07 02:00:00 EST (-0500)",
                "after_normalize": "2002-04-07 03:00:00 EDT (-0400)"
            }
        },
        {
            "input": {
                "zone": "US/Eastern",
                "datetime": "2002-07-07 12:00:00",
                "delta_minutes": 30
            },
            "expected_output": {
                "before_normalize": "2002-07-07 12:30:00 EDT (-0400)",
                "after_normalize": "2002-07-07 12:30:00 EDT (-0400)"
            }
        }
    ]
}
```

---

### Feature 5: Timezone Conversion

**As a developer**, I want to convert a timezone-aware `datetime` from one timezone to another using `astimezone()`, so I can express the same instant in time in any target timezone without manual offset calculation.

**Expected Behavior / Usage:**

*5.1 UTC to local timezone conversion -- Base conversion*

Given a UTC-aware `datetime`, calling `dt.astimezone(target_tz)` returns a new `datetime` representing the same instant in the target timezone, with correct offset and DST abbreviation.

*5.2 Cross-timezone conversion -- Direct conversion between non-UTC timezones*

Given a `datetime` localized to one timezone, calling `dt.astimezone(other_tz)` converts through UTC internally and returns the correct result in the target timezone.

**Test Cases:** `tests/test_cases/feature5_1_utc_conversion.json`

```json
{
    "description": "Test conversion from UTC to various local timezones.",
    "cases": [
        {
            "input": {"utc_datetime": "2002-10-27 06:00:00", "target_zone": "US/Eastern"},
            "expected_output": "2002-10-27 01:00:00 EST (-0500)"
        },
        {
            "input": {"utc_datetime": "2002-10-27 06:00:00", "target_zone": "Asia/Shanghai"},
            "expected_output": "2002-10-27 14:00:00 CST (+0800)"
        },
        {
            "input": {"utc_datetime": "2002-07-07 06:00:00", "target_zone": "US/Eastern"},
            "expected_output": "2002-07-07 02:00:00 EDT (-0400)"
        },
        {
            "input": {"utc_datetime": "2002-10-27 06:00:00", "target_zone": "Europe/London"},
            "expected_output": "2002-10-27 06:00:00 GMT (+0000)"
        },
        {
            "input": {"utc_datetime": "2002-07-07 06:00:00", "target_zone": "Europe/London"},
            "expected_output": "2002-07-07 07:00:00 BST (+0100)"
        }
    ]
}
```

**Test Cases:** `tests/test_cases/feature5_2_cross_timezone.json`

```json
{
    "description": "Test direct conversion between non-UTC timezones.",
    "cases": [
        {
            "input": {
                "source_zone": "US/Eastern",
                "source_datetime": "2002-10-27 06:00:00",
                "target_zone": "Asia/Shanghai"
            },
            "expected_output": "2002-10-27 19:00:00 CST (+0800)"
        },
        {
            "input": {
                "source_zone": "US/Eastern",
                "source_datetime": "2002-07-07 06:00:00",
                "target_zone": "Asia/Shanghai"
            },
            "expected_output": "2002-07-07 18:00:00 CST (+0800)"
        },
        {
            "input": {
                "source_zone": "Asia/Shanghai",
                "source_datetime": "2002-10-27 14:00:00",
                "target_zone": "US/Eastern"
            },
            "expected_output": "2002-10-27 01:00:00 EST (-0500)"
        },
        {
            "input": {
                "source_zone": "Europe/London",
                "source_datetime": "2002-07-07 12:00:00",
                "target_zone": "US/Eastern"
            },
            "expected_output": "2002-07-07 07:00:00 EDT (-0400)"
        }
    ]
}
```

---

### Feature 6: Fixed Offset Timezone

**As a developer**, I want to create timezone objects with fixed UTC offsets (e.g., UTC+8, UTC-5) using `FixedOffset`, so I can represent timezones that do not observe DST with a simple numeric offset.

**Expected Behavior / Usage:**

Calling `pytz.FixedOffset(offset_minutes)` returns a timezone object with a constant UTC offset. The offset is specified in minutes (e.g., 480 for UTC+8, -300 for UTC-5). Fixed-offset timezone objects are cached as singletons: `FixedOffset(480) is FixedOffset(480)` is `True`. The `utcoffset()` method returns a `timedelta` representing the offset. The `dst()` method always returns `timedelta(0)`. The string representation is `pytz.FixedOffset(N)`.

**Test Cases:** `tests/test_cases/feature6_fixed_offset.json`

```json
{
    "description": "Test FixedOffset timezone creation, offset calculation, singleton caching, and datetime formatting.",
    "cases": [
        {
            "input": {"offset_minutes": 480, "datetime": "2002-10-27 06:00:00"},
            "expected_output": {
                "formatted": "2002-10-27 06:00:00 (+0800)",
                "utcoffset": "8:00:00",
                "dst": "0:00:00",
                "repr": "pytz.FixedOffset(480)"
            }
        },
        {
            "input": {"offset_minutes": -300, "datetime": "2002-10-27 06:00:00"},
            "expected_output": {
                "formatted": "2002-10-27 06:00:00 (-0500)",
                "utcoffset": "-1 day, 19:00:00",
                "dst": "0:00:00",
                "repr": "pytz.FixedOffset(-300)"
            }
        },
        {
            "input": {"offset_minutes": 0, "datetime": "2002-10-27 06:00:00"},
            "expected_output": {
                "formatted": "2002-10-27 06:00:00 (+0000)",
                "utcoffset": "0:00:00",
                "dst": "0:00:00",
                "repr": "pytz.FixedOffset(0)"
            }
        },
        {
            "input": {"offset_minutes": 540, "datetime": "2002-10-27 06:00:00"},
            "expected_output": {
                "formatted": "2002-10-27 06:00:00 (+0900)",
                "utcoffset": "9:00:00",
                "dst": "0:00:00",
                "repr": "pytz.FixedOffset(540)"
            }
        },
        {
            "input": {"action": "singleton_check", "offset_minutes": 480},
            "expected_output": {"same_object": true}
        }
    ]
}
```

---

### Feature 7: Country Timezone Query

**As a developer**, I want to look up which timezones are used in a given country by its ISO 3166 country code, so I can present timezone options appropriate for a user's country.

**Expected Behavior / Usage:**

Calling `pytz.country_timezones(country_code)` (or accessing `pytz.country_timezones[country_code]`) returns a list of IANA timezone name strings for the specified country. The country code is case-insensitive (e.g., `'us'` and `'US'` both work). The returned list contains canonical timezone names that can be passed to `pytz.timezone()`. If the country code is not recognized, a `KeyError` is raised.

**Test Cases:** `tests/test_cases/feature7_country_timezones.json`

```json
{
    "description": "Test country timezone lookup by ISO 3166 country code with case-insensitive matching.",
    "cases": [
        {
            "input": {"country_code": "us"},
            "expected_output": {
                "contains": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"],
                "min_length": 5
            }
        },
        {
            "input": {"country_code": "nz"},
            "expected_output": {
                "exact": ["Pacific/Auckland", "Pacific/Chatham"]
            }
        },
        {
            "input": {"country_code": "CH"},
            "expected_output": {
                "exact": ["Europe/Zurich"]
            }
        },
        {
            "input": {"country_code": "cn"},
            "expected_output": {
                "contains": ["Asia/Shanghai"],
                "min_length": 1
            }
        },
        {
            "input": {"country_code": "gb"},
            "expected_output": {
                "contains": ["Europe/London"]
            }
        },
        {
            "input": {"country_code": "XX"},
            "expected_output": {"error": "KeyError"}
        }
    ]
}
```

---

### Feature 8: Error Handling and Exceptions

**As a developer**, I want clear, well-typed exceptions (`UnknownTimeZoneError`, `AmbiguousTimeError`, `NonExistentTimeError`) when timezone operations encounter edge cases, so I can handle errors programmatically and provide meaningful feedback to users.

**Expected Behavior / Usage:**

*8.1 UnknownTimeZoneError -- Raised when a timezone name is not found*

`UnknownTimeZoneError` is a subclass of `KeyError`. It is raised by `timezone()` when the provided zone name does not match any known timezone.

*8.2 AmbiguousTimeError -- Raised during DST fall-back ambiguity*

`AmbiguousTimeError` is raised by `localize()` when `is_dst=None` and the given wall-clock time falls within the DST fall-back overlap period, meaning two distinct UTC instants map to the same local time.

*8.3 NonExistentTimeError -- Raised during DST spring-forward gaps*

`NonExistentTimeError` is raised by `localize()` when `is_dst=None` and the given wall-clock time falls within the DST spring-forward gap, meaning no UTC instant maps to that local time.

**Test Cases:** `tests/test_cases/feature8_1_unknown_timezone.json`

```json
{
    "description": "Test that UnknownTimeZoneError is raised for invalid timezone names.",
    "cases": [
        {
            "input": {"zone": "Unknown/Timezone"},
            "expected_output": {"error": "UnknownTimeZoneError", "is_key_error": true}
        },
        {
            "input": {"zone": "Foo/Bar/Baz"},
            "expected_output": {"error": "UnknownTimeZoneError", "is_key_error": true}
        },
        {
            "input": {"zone": ""},
            "expected_output": {"error": "UnknownTimeZoneError", "is_key_error": true}
        },
        {
            "input": {"zone": "US/Eastern"},
            "expected_output": {"error": null, "zone": "US/Eastern"}
        }
    ]
}
```

**Test Cases:** `tests/test_cases/feature8_2_ambiguous_time.json`

```json
{
    "description": "Test that AmbiguousTimeError is raised for ambiguous times during DST fall-back when is_dst=None.",
    "cases": [
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 01:30:00", "is_dst": null},
            "expected_output": {"error": "AmbiguousTimeError"}
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 01:00:00", "is_dst": null},
            "expected_output": {"error": "AmbiguousTimeError"}
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-10-27 06:00:00", "is_dst": null},
            "expected_output": {"error": null, "formatted": "2002-10-27 06:00:00 EST (-0500)"}
        }
    ]
}
```

**Test Cases:** `tests/test_cases/feature8_3_nonexistent_time.json`

```json
{
    "description": "Test that NonExistentTimeError is raised for non-existent times during DST spring-forward when is_dst=None.",
    "cases": [
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-04-07 02:30:00", "is_dst": null},
            "expected_output": {"error": "NonExistentTimeError"}
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-04-07 02:00:00", "is_dst": null},
            "expected_output": {"error": "NonExistentTimeError"}
        },
        {
            "input": {"zone": "US/Eastern", "datetime": "2002-04-07 03:00:00", "is_dst": null},
            "expected_output": {"error": null, "formatted": "2002-04-07 03:00:00 EDT (-0400)"}
        }
    ]
}
```

---

### Feature 9: Timezone Serialization

**As a developer**, I want to serialize and deserialize timezone objects using `pickle`, so I can store or transmit timezone information and reconstruct identical singleton objects upon deserialization.

**Expected Behavior / Usage:**

All pytz timezone objects (DST-aware, static, UTC, and FixedOffset) support `pickle.dumps()` and `pickle.loads()`. Deserialized objects are the same singleton instances as the originals (i.e., `pickle.loads(pickle.dumps(tz)) is tz` evaluates to `True`). The UTC timezone has an optimized, compact serialization. Serialization preserves the `.zone` attribute and all timezone behavior.

**Test Cases:** `tests/test_cases/feature9_serialization.json`

```json
{
    "description": "Test pickle serialization and deserialization of timezone objects, verifying singleton preservation.",
    "cases": [
        {
            "input": {"zone": "US/Eastern"},
            "expected_output": {"same_object_after_roundtrip": true, "zone": "US/Eastern"}
        },
        {
            "input": {"zone": "UTC"},
            "expected_output": {"same_object_after_roundtrip": true, "zone": "UTC"}
        },
        {
            "input": {"zone": "Asia/Shanghai"},
            "expected_output": {"same_object_after_roundtrip": true, "zone": "Asia/Shanghai"}
        },
        {
            "input": {"zone": "GMT"},
            "expected_output": {"same_object_after_roundtrip": true, "zone": "GMT"}
        },
        {
            "input": {"type": "FixedOffset", "offset_minutes": 480},
            "expected_output": {"same_object_after_roundtrip": true, "repr": "pytz.FixedOffset(480)"}
        },
        {
            "input": {"zone": "UTC", "check": "compact_serialization"},
            "expected_output": {"utc_smaller_than_dst": true}
        }
    ]
}
```

---

### Feature 10: Timezone Collections and Metadata

**As a developer**, I want to access pre-built collections of timezone names (`all_timezones`, `common_timezones`, etc.) and library version information, so I can enumerate available timezones and verify the installed pytz version programmatically.

**Expected Behavior / Usage:**

*10.1 Timezone name collections -- Enumerating available timezones*

`pytz.all_timezones` is a `LazySet` containing every timezone name in the database. `pytz.common_timezones` is a `LazyList` of commonly used timezone names. `pytz.all_timezones_set` is an alias for the set version. These collections are lazily loaded and support standard iteration and membership tests.

*10.2 Version information -- Library metadata*

`pytz.__version__` (or `pytz.VERSION`) returns the version string of the installed pytz library. `pytz.OLSON_VERSION` returns the version of the embedded IANA timezone database.

**Test Cases:** `tests/test_cases/feature10_collections_metadata.json`

```json
{
    "description": "Test timezone name collections (all_timezones, common_timezones) and version metadata.",
    "cases": [
        {
            "input": {"collection": "all_timezones", "check": "contains", "value": "US/Eastern"},
            "expected_output": true
        },
        {
            "input": {"collection": "all_timezones", "check": "contains", "value": "Asia/Shanghai"},
            "expected_output": true
        },
        {
            "input": {"collection": "all_timezones", "check": "contains", "value": "UTC"},
            "expected_output": true
        },
        {
            "input": {"collection": "all_timezones", "check": "min_length"},
            "expected_output": 400
        },
        {
            "input": {"collection": "common_timezones", "check": "contains", "value": "US/Eastern"},
            "expected_output": true
        },
        {
            "input": {"collection": "common_timezones", "check": "is_list"},
            "expected_output": true
        },
        {
            "input": {"attribute": "__version__", "check": "is_string"},
            "expected_output": true
        },
        {
            "input": {"attribute": "OLSON_VERSION", "check": "is_string"},
            "expected_output": true
        }
    ]
}
```

---

## Deliverables

For each feature, the implementation should include:

1. **A runnable script** that reads input from stdin and prints results to stdout, matching the format described in the test cases above.

2. **Automated tests** covering all features. All test case data files (`*.json`) should be placed under `tests/test_cases/`. All testing scripts should be placed under `tests/`. The implementation approach for the testing scripts is flexible -- any combination of shell scripts and helper scripts is acceptable, as long as a single entry point `tests/test.sh` is provided. Crucially, running `bash tests/test.sh` should execute the full test suite and output the result of each individual test case into a separate file under the `tests/stdout/` directory. The naming convention for these output files MUST be `tests/stdout/{filename.stem}@{case_index.zfill(3)}.txt` (e.g., the first case in `feature1_[name].json` should write its output to `tests/stdout/feature1_[name]@000.txt`). The content of these generated `.txt` files should consist **solely** of the program's actual output for that specific test case, with **no** additional information such as pass/fail summaries, test case names, or status messages, so they can be directly compared against the expected outputs externally.
