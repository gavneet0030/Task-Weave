#include "taskweave/bounded_queue.hpp"

#include <atomic>
#include <iostream>
#include <thread>

int main() {
    taskweave::BoundedQueue<int> queue(2);
    std::atomic<int> count{0};
    std::atomic<long long> checksum{0};

    std::thread consumer([&] {
        while (const auto item = queue.pop()) {
            checksum.fetch_add(*item);
            count.fetch_add(1);
        }
    });

    std::thread producer([&] {
        for (int value = 1; value <= 5; ++value) {
            if (!queue.push(value)) {
                break;
            }
        }
        queue.close();
    });

    producer.join();
    consumer.join();

    std::cout << "TaskWeave native bounded-queue demo\n";
    std::cout << "Items consumed: " << count.load() << '\n';
    std::cout << "Checksum: " << checksum.load() << '\n';

    if (count.load() != 5 || checksum.load() != 15) {
        std::cerr << "Native queue verification failed\n";
        return 1;
    }

    std::cout << "Native queue verification: PASS\n";
    return 0;
}