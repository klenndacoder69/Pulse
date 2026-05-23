#include "crow_all.h"
#include <sw/redis++/redis++.h>
#include <iostream>

int main() {
    crow::SimpleApp app;

    // redis ingest url
    const char *redis_env = std::getenv("REDIS_HOST");
    std::string redis_host = redis_env ? redis_env : "127.0.0.1";
    std::string redis_url = "tcp://" + redis_host + ":6379";

    auto redis = sw::redis::Redis(redis_url);

    CROW_ROUTE(app, "/ingest").methods(crow::HTTPMethod::POST)
    ([&redis](const crow::request& req){
        
        auto log_data = crow::json::load(req.body);
        if (!log_data) {
            return crow::response(400, "Invalid JSON");
        }

        try {
	// queue name
            redis.lpush("telemetry_queue", req.body);
        } catch (const sw::redis::Error &err) {
            std::cerr << "Redis Error: " << err.what() << std::endl;
            return crow::response(500, "Internal Server Error: Cache Unavailable");
        }
        
        std::cout << "Cached log in Redis: " << req.body << std::endl;
        return crow::response(202, "Log accepted for processing");
    });

    app.port(8080).multithreaded().run();
}
