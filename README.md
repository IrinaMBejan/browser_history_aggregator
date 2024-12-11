# Browser History Aggregator
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

Browser History Aggregator [SyftBox](https://github.com/OpenMined/syft) API.

## Aggregating Results with `browser_history_aggregator`

The [`browser_history_member`](https://github.com/VivekSil/browser_history_member) app writes intermediary outputs to a folder where only the aggregator has access. The aggregator app, [`browser_history_aggregator`](https://github.com/IrinaMBejan/browser_history_aggregator), computes the final results and pushes them to a file where they can be used by the static website.

## Usage

**1. Clone the API**

```bash
git clone https://github.com/IrinaMBejan/browser_history_aggregator
```

**2. Agree on roles in the Browser History Federated Learning WorkFlow**

Aggregator: `<aggregator@email.com>`; 
Clients: `<client1@email.com>`,`<client2@email.com>`

Details:
- Aggregator has access to the `private` folder of each clients folder where the [`browser_history_member`](https://github.com/VivekSil/browser_history_member) app writes intermediary outputs
- Only the Aggregator must install and run the `browser_history_aggregator` app.
- Clients have to install and run the [`browser_history_member`](https://github.com/VivekSil/browser_history_member) app (please read the README of the app for more details).


**3. Run the app [only for Aggregator role]**
Copy the app to the SyftBox data directory:
```bash
cp -r ./browser_history_aggregator <SYFTBOX_DATADIR>/apis/  # default: ~/SyftBox
```

> [!NOTE]
> `<SYFTBOX_DATADIR>` refers to the SyftBox data directory, according to your SyftBox installation (default: `$HOME/SyftBox`).

Run the SyftBox environment:
```bash
curl -LsSf https://syftbox.openmined.org/install.sh | sh
```

Then, after the installation is complete and the SyftBox environment you should be able to see the app running:
```bash
Running browser_history with ... at '...'
```
- The aggregator app will write the final results by aggregating private information from all the clients, to a file in the specified output directory: `<SYFTBOX_DATADIR>/datasites/<aggregator_email>/public/browser_history_agg/outputs`.
- These results can then be used by the static website to render the view at `<SYFTBOX_DATADIR>/datasites/<aggregator_email>/public/browser_history_agg/index.html`.

**4. Monitoring the FL experiment**

- Visit the aggregator's dashboard to monitor the FL progress
which is available at `http://server_url/datasites/<aggregator_email>/public/browser_history_agg/`

The `server_url` depends on which the server the client is running on.
- `syftbox.openmined.org` (for the public server)
- `localhost:5001` (when running locally, with default configuration)

### Example
Visit our [Browser History Aggregator Test](https://syftbox.openmined.org/datasites/irina@openmined.org/browser_history_agg/)!

### Find Your Learning Mate
Join the Browser History Community as a client!
Follow the instructions and installations here!
Then go to the [Browser History Aggregator Test](https://syftbox.openmined.org/datasites/irina@openmined.org/browser_history_agg/) and type yout email in the textbox at the bottom to *Find Your Learning Mate*!
Get in touch with your learning mate and start learning together!

## Features
- macOS
- Linux
- Windows

### Requirements
It requires giving to Terminal "Full Disk Access" (if you read the code, you will see why). 

SyftBox is required to run the app.

### Prerequisites
- python 3.8+
- syftbox