#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <numeric>
#include <thread>
#include <chrono>
#include <unistd.h>
#include <curl/curl.h>

const char* env_url = std::getenv("API_URL");
const std::string API_URL = env_url ? env_url : "http://localhost:8080/ingest";

struct CPUData {
	size_t active_time;
	size_t total_time;
};

CPUData read_sys_cpu() {
	std::ifstream file("/proc/stat");
	std::string line;
	std::getline(file, line);
	std::istringstream ss(line);
	std::string cpu_label;
	ss >> cpu_label;

	std::vector<size_t> times;
	size_t time;
	while (ss >> time) {
		times.push_back(time);
    }

    // times[0]=user, [1]=nice, [2]=system, [3]=idle, [4]=iowait, [5]=irq, [6]=softirq, [7]=steal
    size_t idle_time = times[3] + times[4];
    size_t total_time = std::accumulate(times.begin(), times.end(), 0ULL);
    size_t active_time = total_time - idle_time;

    return {active_time, total_time};
}

void send(const std::string& json) {
    CURL *curl;
    curl = curl_easy_init();
    if(curl) {
        struct curl_slist *headers = NULL;
        headers = curl_slist_append(headers, "Content-Type: application/json");

        curl_easy_setopt(curl, CURLOPT_URL, API_URL.c_str());
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json.c_str());
        // Fail fast: abort if connection isn't established within 3s
        curl_easy_setopt(curl, CURLOPT_CONNECTTIMEOUT, 3L);
        // Fail fast: abort the whole transfer if it takes longer than 5s
        curl_easy_setopt(curl, CURLOPT_TIMEOUT, 5L);

        CURLcode res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            fprintf(stderr, "send failed: %s\n", curl_easy_strerror(res));
        }

        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
    }
    // Note: curl_global_cleanup() is intentionally NOT called here.
    // It must only be called once at program exit (see main).
}

int main(){
    // Disable stdout buffering so Docker logs stream in real-time
    setvbuf(stdout, NULL, _IONBF, 0);

	char hostname[64];
	if(gethostname(hostname, sizeof(hostname)) != 0) {
		std::cerr << "Failed to get hostname" << std::endl;
		return 1;
	}
	std::string server_id(hostname);
	std::cout << "Reading /proc/stat metrics directly. Press Ctrl+C to stop \n\n";

	CPUData prev_cpu = read_sys_cpu();

	while (true) {
		std::this_thread::sleep_for(std::chrono::seconds(1));
		CPUData curr_cpu = read_sys_cpu();
		
		// calculate the delta
		size_t active_delta = curr_cpu.active_time - prev_cpu.active_time;
        size_t total_delta = curr_cpu.total_time - prev_cpu.total_time;

		double cpu_percentage = 100.0 * static_cast<double>(active_delta) / total_delta;
	
		// "healthy" as default status
		std::string status = "healthy";

		if (cpu_percentage > 90.0) status = "critical";
        else if (cpu_percentage > 75.0) status = "warning";

        std::string json_payload = R"({"server_id": ")" + server_id + 
                                   R"(", "cpu_usage": )" + std::to_string(cpu_percentage) + 
                                   R"(, "status": ")" + status + R"("})";

        printf("[%s] CPU: %5.1f%% | %-8s\n", server_id.c_str(), cpu_percentage, status.c_str());
        send(json_payload);

        prev_cpu = curr_cpu;
	}
	curl_global_cleanup();
	return 0;	
}
