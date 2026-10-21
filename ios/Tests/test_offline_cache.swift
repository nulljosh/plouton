// Standalone self-check for OfflineCache, compiled against the real file:
// cat ios/API/OfflineCache.swift ios/Tests/test_offline_cache.swift | swift -
import Foundation

OfflineCache.directory = FileManager.default.temporaryDirectory.appendingPathComponent("talli-offline-check-\(UUID().uuidString)")

func request(_ path: String, _ method: String = "GET") -> URLRequest {
    var r = URLRequest(url: URL(string: "https://talli.jaybulb.com/\(path)")!)
    r.httpMethod = method
    return r
}

let body = Data(#"{"ok":true}"#.utf8)
OfflineCache.save(body, for: request("api/rdsp-tracker"))
precondition(OfflineCache.load(for: request("api/rdsp-tracker")) == body, "FAIL GET round trip")
print("ok  GET body comes back")

OfflineCache.save(body, for: request("api/report-status", "POST"))
precondition(OfflineCache.load(for: request("api/report-status", "POST")) == nil, "FAIL POST cached")
print("ok  writes are never cached")

OfflineCache.save(body, for: request("api/widget-token"))
precondition(OfflineCache.load(for: request("api/widget-token")) == nil, "FAIL token cached")
print("ok  tokens are never cached")

OfflineCache.clear()
precondition(OfflineCache.load(for: request("api/rdsp-tracker")) == nil, "FAIL clear")
print("ok  sign-out clears it")

print("all offline cache checks passed")
