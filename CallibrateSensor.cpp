#include <iostream>
#include <fstream>
#include <vector>
#include "json.hpp"  // Include nlohmann/json
using json = nlohmann::json;

const int NUM_CHANNELS = 8;

std::vector<int> load_from_file(const std::string& filename) {
    std::ifstream file(filename);
    json j;
    file >> j;

    std::vector<int> values;
    for (const auto& key : {"F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"}) {
        values.push_back(j["spectral data"][key]);
    }
    return values;
}

int main(){
    std::vector<int> normalized(8);
    std::vector<int> redFace = load_from_file("redSideLED.json");
    std::vector<int> whiteRef = load_from_file("whiteReference.json");
    std::vector<int> darkRef = load_from_file("darkReference.json");
    for (int i = 0; i < NUM_CHANNELS; i++) {
        normalized[i] = (redFace[i] - darkRef[i]) / float(whiteRef[i] - darkRef[i]);
    }
    return 0;
}
