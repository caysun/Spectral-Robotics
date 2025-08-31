#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <string>
#include "json.hpp"  // Include nlohmann/json 

using json = nlohmann::json;

const std::vector<std::string> BANDS = {
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"
};

// Load and average spectral data from a JSON file
std::vector<std::map<std::string, std::string>> load(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        std::cerr << "Error opening file: " << filename << "\n";
        exit(1);
    }

    json j;
    file >> j;
    std::vector<std::map<std::string, std::string>> result(j.size());

    int index = 0;
    for(const auto& entry : j){
        for (const auto& band : BANDS) {
            result[index][band] = std::to_string(entry[band].get<float>());
        }
        result[index]["label"] = entry["label"].get<std::string>();
        index++;
    }    

    return result;
}

// Normalize sample data using white and dark reference formula
std::map<std::string, float> normalize(
    const std::map<std::string, std::string>& sample,
    const std::map<std::string, std::string>& white,
    const std::map<std::string, std::string>& dark)
{
    std::map<std::string, float> normalized;
    for (const auto& band : BANDS) {
        if(band == "Clear" || band == "Near IR"){
            continue;
        }
        double numerator = std::stof(sample.at(band)) - std::stof(dark.at(band));
        double denominator = std::stof(white.at(band)) - std::stof(dark.at(band));
        normalized[band] = (denominator != 0.0f) ? numerator / denominator : 0.0f;
    }
    return normalized;
}

int main() {

    auto sample = load("MLpaperReadings/test.json");
    auto whiteRef = load("MLpaperReadings/test.json");
    auto darkRef = load("MLpaperReadings/test.json");

    
    for(int i=0; i<sample.size(); i++){
        auto reflectance = normalize(sample[i], whiteRef[0], darkRef[2]);
        // Build JSON object to add to file
        json output;
        for (const auto& band : BANDS) {
            output[band] = reflectance[band];
        }
        output["label"] = sample[i]["label"];

        // Read existing data and check if file exists
        json existing_data = json::array();
        std::ifstream inFile("trainingData/calibratedReadings.json");
        if (inFile) {
            inFile >> existing_data;
            inFile.close();
            if (!existing_data.is_array()) {
                printf("Error: Existing data is not an array.\n");
                return 1; // Error: existing data is not an array
            }
        }

        // Append the new reading
        existing_data.push_back(output);

        // Write each object on its own line
        std::ofstream outFile("trainingData/calibratedReadings.json");
        outFile << "[\n";

        for (size_t i = 0; i < existing_data.size(); ++i) {
            outFile << "  "; // indent for readability
            outFile << existing_data[i].dump(); // compact object on one line
            if (i != existing_data.size() - 1) {
                outFile << ",";  // comma between objects
            }
            outFile << "\n"; // newline after each object
        }

        outFile << "]";
        outFile.close();
    }

    std::cout << "Successfully calibrated readings";

    return 0;
}
