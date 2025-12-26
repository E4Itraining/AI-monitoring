-- Fluent-bit Lua enrichment script
-- Adds missing fields and normalizes log structure

function enrich_log(tag, timestamp, record)
    -- Add timestamp if missing
    if record["@timestamp"] == nil then
        record["@timestamp"] = os.date("!%Y-%m-%dT%H:%M:%S.000Z")
    end

    -- Normalize log level
    if record["level"] ~= nil then
        record["level"] = string.upper(record["level"])
    end

    -- Extract trace context if present
    if record["trace_id"] == nil and record["traceId"] ~= nil then
        record["trace_id"] = record["traceId"]
    end

    if record["span_id"] == nil and record["spanId"] ~= nil then
        record["span_id"] = record["spanId"]
    end

    -- Add source info
    record["collector"] = "fluent-bit"
    record["collector_version"] = "2.2.3"

    return 1, timestamp, record
end
