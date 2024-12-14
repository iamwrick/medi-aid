<h1 align="center">Welcome to Agentic Emergency Medical Aid Provider (Project Dr.Pepper) 👋</h1>
<p>
  <img alt="Version" src="https://img.shields.io/badge/version-0.0.1-blue.svg?cacheSeconds=2592000" />
  <a href="#" target="_blank">
    <img alt="License: MIT License" src="https://img.shields.io/badge/License-MIT License-yellow.svg" />
  </a>
</p>

# Sample Agentic System for Life-Saving Medical Emergency
> In the critical moments of a medical emergency, every second counts. The effectiveness of the response can mean the difference between life and death. Yet, current emergency response systems often face significant challenges such as delayed response times, miscommunication, and inefficient resource allocation. These issues can lead to preventable loss of life and exacerbate medical complications.

## Key features:

- Real-Time Situation Assessment
Using AI and IoT sensors, the system can assess the severity of an emergency by analyzing real-time data (e.g., vitals from wearable devices or environmental conditions).

- Dynamic Resource Allocation
Intelligent algorithms ensure the fastest and most appropriate allocation of medical resources, such as ambulances, hospitals, or on-call doctors, based on proximity, capacity, and expertise.

- Autonomous Communication
The system automatically contacts emergency services, provides detailed information about the patient’s condition, and even communicates with nearby medical facilities to prepare for the arrival of the patient.

- Personalized Emergency Response
By integrating patient medical histories and health profiles, the solution provides tailored recommendations for care during transit and on-site.

- Scalable and Reliable Systems
Built on cloud and edge technologies, the agentic solution ensures high availability and scalability, making it suitable for urban and rural settings alike.

## Technologies used:

- CrewAI: For intelligent task automation and agent-driven analysis.
- OpenAI Models: For natural language understanding and advanced data processing.
- Google Maps: For searching real-time location, hospitals, and emergency services.
- LangChain: For enhancing the NLP pipeline, enabling sophisticated data extraction and analysis.

## Setup:

1. Clone the repository to your local machine:

`git clone https://github.com/iamwrick/medi-aid.git`

2. Navigate to the project directory:

`cd medi-aid`

3. Install the package and its dependencies:

`pip install .`
This will install the medi-aid package and all of its dependencies listed in the requirements.txt file.

4. Create a .env file: In the project root directory, create a .env file to store your API keys. Add the following lines to the .env file:

`OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here`

5. Make sure to replace your_openai_api_key_here and your_google_maps_api_key_here with your actual API keys. 
Note: The .env file is used to securely store environment variables, and it should not be committed to the repository. Ensure that it is added to .gitignore to prevent accidental exposure of your keys.

<!-- Optional: Set up the development environment -->

If you want to set up the project for development, you can install the development dependencies by running the following command:

`pip install .[dev]`

6. Run the src/main.py first and then run the tests/simulation_runner.py. The simulation will try to replicate real-life emergency and the agentic framework will start to take actions. 


## Results
If everything executed successfully, you will find multiple reports generated under the reports directory. The main report will be named something like:
simulation_summary_xxxxxxx_xxxx.txt

### **Summary Reports**
The summary report provides an overview of the Scenario and Response, including detailed incident data. Below is an example of the reported data:
```json
{
  "patient_age": 30,
  "patient_gender": "male",
  "chief_complaint": "severe shortness of breath",
  "location": {
    "lat": 40.7829,
    "lng": -73.9654,
    "description": "50 85th St Transverse, New York, NY 10024, USA",
    "nearest_hospital": {
      "name": "NY-Presbyterian Hospital",
      "address": "1305 York Ave, New York",
      "rating": 4.3
    }
  },
  "vitals": {
    "heart_rate": 129,
    "blood_pressure_systolic": 113,
    "blood_pressure_diastolic": 81,
    "spo2": 90,
    "respiratory_rate": 17
  }
}
```
### **Additional Reports**
Subsequent reports include detailed insights about the patient's condition and vital signs.



## Author

👤 **Wrick Talukdar**

* Github: [@iamwrick](https://github.com/iamwrick)
* LinkedIn: [@https:\/\/www.linkedin.com\/in\/wrick-talukdar\/](https://linkedin.com/in/https:\/\/www.linkedin.com\/in\/wrick-talukdar\/)

## Blog

* Blog: []


## Show your support

Give a ⭐️ if this project helped you!

