#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <string>
#include "json.hpp"  // Include nlohmann/json 

using json = nlohmann::json;

const std::vector<std::string> BANDS = {
    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "Clear", "Near IR"
};

// Load and average spectral data from a JSON file
std::map<std::string, float> load_and_average(const std::string& filename) {
    std::ifstream file(filename);
    if (!file) {
        std::cerr << "Error opening file: " << filename << "\n";
        exit(1);
    }

    json j;
    file >> j;
    std::map<std::string, float> sum;
    for (const auto& band : BANDS) sum[band] = 0.0f;

    for (const auto& entry : j) {
        const auto& spectral = entry["spectral data"];
        for (const auto& band : BANDS) {
            sum[band] += spectral[band].get<float>();
        }
    }

    int count = j.size();
    for (auto& pair : sum) {
        pair.second /= count;
    }

    return sum;
}

// Normalize sample data using white and dark reference formula
std::map<std::string, float> normalize(
    const std::map<std::string, float>& sample,
    const std::map<std::string, float>& white,
    const std::map<std::string, float>& dark)
{
    std::map<std::string, float> normalized;
    for (const auto& band : BANDS) {
        if(band == "Clear" || band == "Near IR"){
            normalized[band] = sample.at(band);
            continue;
        }
        float numerator = sample.at(band) - dark.at(band);
        float denominator = white.at(band) - dark.at(band);
        normalized[band] = (denominator != 0.0f) ? numerator / denominator : 0.0f;
    }
    return normalized;
}

int main() {
    auto redSample = load_and_average("sampleReadings/test.json");
    auto whiteRef = load_and_average("sampleReadings/whiteRef.json");
    auto darkRef = load_and_average("sampleReadings/darkRef.json");

    auto reflectance = normalize(redSample, whiteRef, darkRef);

    // Build JSON object to add to file
    json output;
    output["spectral reflectance"] = json::object();
    for (const auto& band : BANDS) {
        output["spectral reflectance"][band] = reflectance[band];
    }
    output["spectral reflectance"]["Label"] = "teal face";

    // Read existing data and check if file exists
    json existing_data = json::array();
    std::ifstream inFile("calibratedReadings.json");
    if (inFile) {
        inFile >> existing_data;
        inFile.close();
        if (!existing_data.is_array()) {
            std::cerr << "Error: file does not contain a JSON array.\n";
            return 1;
        }
    }

    // Append the new reading
    existing_data.push_back(output);

    // Write updated array back to file
    std::ofstream outFile("calibratedReadings.json");
    outFile << existing_data.dump(2);  // Pretty print with 2-space indentation
    outFile.close();

    std::cout << "Successfully calibrated readings";

    return 0;
}
