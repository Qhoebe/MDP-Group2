package com.example.androidcontroller;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.Fragment;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import android.os.Handler;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

import com.example.androidcontroller.service.BluetoothConnectionService;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Set;
import java.util.UUID;

public class BluetoothFragment extends Fragment {
    private static final String TAG = "BluetoothFragment";

    private BluetoothAdapter btAdapter;
    private boolean btOn;


    private Button btnToggleBluetooth;
    private Button btnSearchBluetooth;
    private BluetoothDiscoveredListViewAdapter discoveredDevicesAdapter;
    private List<String> discoveredDevicesAdapterData;
    private BluetoothPairedListViewAdapter pairedDevicesAdapter;
    private List<String> pairedDevicesAdapterData;


    private HashMap<String, BluetoothDevice> pairedDevices;
    private HashMap<String, BluetoothDevice> discoveredDevices;


    private BluetoothConnectionService btConnectionService;
    private static final UUID MY_UUID_INSECURE =
            UUID.fromString("b223f3ef-cd76-44f5-8483-afa54eb791d3");
    private boolean retryConnection = false;
    private String curDeviceAddress;
    private Handler reconnectionHandler = new Handler();
    private Button curConnectionBtn;


    private boolean initializedBCastReceivers = false;


    Button sendMsgBtn;
    TextView receivedTextView;
    EditText txtMsgToSend;


    private static final String ARG_PARAM1 = "param1";
    private static final String ARG_PARAM2 = "param2";


    private String mParam1;
    private String mParam2;


    public static BluetoothFragment newInstance(String param1, String param2) {
        BluetoothFragment fragment = new BluetoothFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, param1);
        args.putString(ARG_PARAM2, param2);
        fragment.setArguments(args);
        return fragment;
    }

    public BluetoothFragment() {
        btOn = false;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        discoveredDevices = new HashMap<String, BluetoothDevice>();
        discoveredDevicesAdapterData = new ArrayList<>();
        pairedDevices = new HashMap<String, BluetoothDevice>();
        pairedDevicesAdapterData = new ArrayList<>();

        IntentFilter btPairingFilter = new IntentFilter(BluetoothDevice.ACTION_BOND_STATE_CHANGED);
        getActivity().registerReceiver(btPairingReceiver, btPairingFilter);

        if(btConnectionService == null){
           btConnectionService = new BluetoothConnectionService(getContext());
        }

        if(!initializedBCastReceivers){

            LocalBroadcastManager.getInstance(getContext()).registerReceiver(bluetoothMsgReceiver, new IntentFilter("incomingBTMessage"));
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(sendBluetoothReceiver, new IntentFilter("sendBTMessage"));
            LocalBroadcastManager.getInstance(getContext()).registerReceiver(btConnectionUpdateReceiver, new IntentFilter("connectionBTStatus"));
            initializedBCastReceivers = true;
        }

    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {

        View rootView = inflater.inflate(R.layout.fragment_bluetooth, container, false);

        btnToggleBluetooth = rootView.findViewById(R.id.bluetooth_btn_toggle);
        btnToggleBluetooth.setOnClickListener(v -> {
            toggleBluetooth();
        });
        btnSearchBluetooth = rootView.findViewById(R.id.bluetooth_btn_search);
        btnSearchBluetooth.setOnClickListener(v -> {
            searchBluetooth();
        });

        ListView discoveredDevicesListView = (ListView) rootView.findViewById(R.id.bluetooth_device_list);
        discoveredDevicesAdapter = new BluetoothDiscoveredListViewAdapter(getContext(), R.layout.bt_device_list_layout, discoveredDevicesAdapterData);
        discoveredDevicesListView.setAdapter(discoveredDevicesAdapter);

        ListView pairedDevicesListView = (ListView) rootView.findViewById(R.id.paired_device_list);
        pairedDevicesAdapter = new BluetoothPairedListViewAdapter(getContext(), R.layout.bt_paired_device_list_layout, pairedDevicesAdapterData);
        pairedDevicesListView.setAdapter(pairedDevicesAdapter);

        initializeBluetooth();


        sendMsgBtn = (Button) rootView.findViewById(R.id.temp_btnsend);
        receivedTextView = (TextView) rootView.findViewById(R.id.temp_btreceivedmsgs);
        txtMsgToSend = (EditText) rootView.findViewById(R.id.temp_msginput);

        sendMsgBtn.setOnClickListener(v -> {
            byte[] bytes = txtMsgToSend.getText().toString().getBytes(Charset.defaultCharset());
            btConnectionService.write(bytes);
            txtMsgToSend.setText("");
        });
        return rootView;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
    }


    private void initializeBluetooth() {
        btAdapter = BluetoothAdapter.getDefaultAdapter();
        if (btAdapter == null) {
            showShortToast("Bluetooth is not supported");
            return;
        }

        btnToggleBluetooth.setEnabled(true);
        if (btAdapter.isEnabled()) {
            btOn = true;
        }

        Set<BluetoothDevice> paired = btAdapter.getBondedDevices();
        for (BluetoothDevice device : paired) {
            if (!pairedDevices.containsKey(device.getAddress())) {
                pairedDevices.put(device.getAddress(), device);
                pairedDevicesAdapterData.add(device.getAddress());
                pairedDevicesAdapter.updateList(pairedDevicesAdapterData);
            }
        }

        updateBluetoothControlButtons();
    }

    private void toggleBluetooth() {
        btOn = !btOn;
        if (btOn) {
            btAdapter.enable();
        } else {
            btAdapter.disable();
        }
        updateBluetoothControlButtons();
    }

    private void searchBluetooth() {
        if (btOn) {
            discoveredDevices.clear();
            discoveredDevicesAdapter.clear();

            if (btAdapter.isDiscovering()) {
                btAdapter.cancelDiscovery();
            }

            Intent discoverableIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
            discoverableIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 300);
            startActivity(discoverableIntent);

            checkLocationPermission();
            btAdapter.startDiscovery();

            IntentFilter filter = new IntentFilter();
            filter.addAction(BluetoothDevice.ACTION_FOUND);
            filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_STARTED);
            filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED);
            getContext().registerReceiver(btDiscoveryReceiver, filter);
        } else {
            showShortToast("Please enable bluetooth first");
            Log.d(TAG, "Tried to discover without bluetooth enabled");
        }
    }

    private final BroadcastReceiver btDiscoveryReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();

            if (BluetoothAdapter.ACTION_DISCOVERY_STARTED.equals(action)) {

                showShortToast("Discovering Devices");

            } else if (BluetoothAdapter.ACTION_DISCOVERY_FINISHED.equals(action)) {

                showShortToast("Discovery Ended");

            } else if (BluetoothDevice.ACTION_FOUND.equals(action)) {

                BluetoothDevice device = (BluetoothDevice) intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                if (device != null) {
                    String deviceName = device.getName();
                    String deviceAddress = device.getAddress();


                    if (discoveredDevices.containsKey(deviceAddress)) return;

                    if(pairedDevices.containsKey(deviceAddress)) return;

                    discoveredDevices.put(deviceAddress, device);
                    discoveredDevicesAdapterData.add(deviceAddress);
                    discoveredDevicesAdapter.updateList(discoveredDevicesAdapterData);
                    Log.d(TAG, "Found device: " + device.getName() + ", " + device.getAddress());
                }
            }
        }
    };

    private final BroadcastReceiver btPairingReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            final String action = intent.getAction();

            if (action.equals(BluetoothDevice.ACTION_BOND_STATE_CHANGED)) {
                BluetoothDevice mDevice = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);

                if (mDevice.getBondState() == BluetoothDevice.BOND_BONDED) {
                    Log.d(TAG, "BroadcastReceiver: BOND_BONDED.");
                    setPaired(mDevice);
                }

                if (mDevice.getBondState() == BluetoothDevice.BOND_BONDING) {
                    Log.d(TAG, "BroadcastReceiver: BOND_BONDING.");
                }

                if (mDevice.getBondState() == BluetoothDevice.BOND_NONE) {
                    Log.d(TAG, "BroadcastReceiver: BOND_NONE.");
                }
            }
        }
    };


    private void updateBluetoothControlButtons() {
        if (btOn) {
            btnToggleBluetooth.setText("Bluetooth: ON");
            btnSearchBluetooth.setEnabled(true);
        } else {
            btnToggleBluetooth.setText("Bluetooth: OFF");
            btnSearchBluetooth.setEnabled(false);
        }
    }


    public void checkLocationPermission() {
        if (ContextCompat.checkSelfPermission(getContext(), Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(getContext(), Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            return;
        }
        showShortToast("Please grant locations permissions first!");

        requestPermissionLauncher.launch(Manifest.permission.ACCESS_FINE_LOCATION);
        requestPermissionLauncher.launch(Manifest.permission.ACCESS_COARSE_LOCATION);
    }

    private void disconnectBluetooth(){
        btConnectionService.disconnect();
    }

    private boolean connectBluetooth(String macAddress) {

        showShortToast("Connect to: " + macAddress);
        BluetoothDevice btDevice = pairedDevices.get(macAddress);
        if(btDevice == null){
            showShortToast("Bluetooth device not paired");
            return false;
        }
        try{
            btConnectionService.startClient(btDevice);
            curDeviceAddress = macAddress;
            return true;
        }catch(Exception e){
            showShortToast("An error occurred while attempting to start connection");
            e.printStackTrace();
            return false;
        }
    }

    private void pairBluetooth(String macAddress) {
        try {
            if (pairedDevices.containsKey(macAddress)) {
                Log.d(TAG, "Pair bluetooth: Device " + macAddress + " is already paired");
                return;
            }
            BluetoothDevice device = discoveredDevices.get(macAddress);
            if (device == null) {
                Log.d(TAG, "Pair bluetooth: Device " + macAddress + " is not found");
                return;
            }

            if (Build.VERSION.SDK_INT > Build.VERSION_CODES.JELLY_BEAN_MR2) {
                Log.d(TAG, "Trying to pair with " + macAddress);
                boolean bonded = device.createBond();
                if (!bonded) {
                    Log.e(TAG, "An error occurred while trying to pair with device " + macAddress);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private ActivityResultLauncher<String> requestPermissionLauncher =
            registerForActivityResult(new ActivityResultContracts.RequestPermission(), isGranted -> {
                if (isGranted) {
                    showShortToast("Location permissions granted");
                } else {
                }
            });

    private class BluetoothDiscoveredListViewAdapter extends ArrayAdapter<String> {
        private List<String> items;

        public BluetoothDiscoveredListViewAdapter(@NonNull Context context, int resource, @NonNull List<String> objects) {
            super(context, resource, objects);
            items = objects;
        }

        public void updateList(List<String> list) {
            items = list;
            this.notifyDataSetChanged();
        }

        @NonNull
        @Override
        public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
            if (convertView == null) {
                convertView = LayoutInflater.from(getContext()).inflate(R.layout.bt_device_list_layout, parent, false);
            }
            BluetoothDevice btDevice = discoveredDevices.get(items.get(position));

            String deviceName = btDevice.getName();
            String deviceMAC = btDevice.getAddress();

            if (deviceName == null || deviceName.isEmpty()) {
                deviceName = "Unnamed Device";
            }
            if (deviceMAC == null || deviceMAC.isEmpty()) {
                deviceMAC = "No address found";
            }

            TextView btDeviceTitleTxt = (TextView) convertView.findViewById(R.id.bt_list_title);
            TextView btDeviceMACTxt = (TextView) convertView.findViewById(R.id.bt_list_macaddr);
            Button btnConnect = (Button) convertView.findViewById(R.id.bluetooth_pair_btn);

            btDeviceTitleTxt.setText(deviceName);
            btDeviceMACTxt.setText(deviceMAC);
            btnConnect.setOnClickListener(v -> {
                pairBluetooth(items.get(position));
            });
            return convertView;
        }
    }

    private Runnable reconnectRunnable =new Runnable() {
        @Override
        public void run() {
            try {
                if(!BluetoothConnectionService.isConnected && retryConnection){
                    connectBluetooth(curDeviceAddress);
                }
                reconnectionHandler.removeCallbacks(reconnectRunnable);
            }catch (Exception e){
                Log.e(TAG, "run: An error occurred while running reconnectRunnable");
                showShortToast("Error reconnecting, retrying in 5s");
                e.printStackTrace();
            }
        }
    };

    private void showShortToast(String msg) {
        Toast.makeText(getActivity(), msg, Toast.LENGTH_LONG).show();
    }

    private void showLongToast(String msg) {
        Toast.makeText(getActivity(), msg, Toast.LENGTH_SHORT).show();
    }

    private void sendIntent(String intentAction, String content){
        Intent sendingIntent = new Intent(intentAction);
        sendingIntent.putExtra("msg", content);
        LocalBroadcastManager.getInstance(getContext()).sendBroadcast(sendingIntent);
    }

    private class BluetoothPairedListViewAdapter extends ArrayAdapter<String> {
        private List<String> items;

        public BluetoothPairedListViewAdapter(@NonNull Context context, int resource, @NonNull List<String> objects) {
            super(context, resource, objects);
            items = objects;
        }

        public void updateList(List<String> list) {
            items = list;
            this.notifyDataSetChanged();
        }

        @NonNull
        @Override
        public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
            if (convertView == null) {
                convertView = LayoutInflater.from(getContext()).inflate(R.layout.bt_paired_device_list_layout, parent, false);
            }
            BluetoothDevice btDevice = pairedDevices.get(items.get(position));

            String deviceName = btDevice.getName();
            String deviceMAC = btDevice.getAddress();

            if (deviceName == null || deviceName.isEmpty()) {
                deviceName = "Unnamed Device";
            }
            if (deviceMAC == null || deviceMAC.isEmpty()) {
                deviceMAC = "No address found";
            }

            TextView btDeviceTitleTxt = (TextView) convertView.findViewById(R.id.bt_list_paired_title);
            TextView btDeviceMACTxt = (TextView) convertView.findViewById(R.id.bt_list_paired_macaddr);
            Button btnConnect = (Button) convertView.findViewById(R.id.bluetooth_connect_btn);

            btDeviceTitleTxt.setText(deviceName);
            btDeviceMACTxt.setText(deviceMAC);
            btnConnect.setOnClickListener(v -> {
                if(btnConnect.getText().equals("Disconnect")){
                    retryConnection = false;
                    disconnectBluetooth();
                    btnConnect.setText("Connect");
                    sendIntent("updateRoboCarState","finished");
                    return;
                }
                boolean connectSuccess = connectBluetooth(items.get(position));
                if(connectSuccess){
                    btnConnect.setText("Wait..");
                    retryConnection = true;
                    curConnectionBtn = btnConnect;
                }
            });
            return convertView;
        }
    }

    private void setPaired(BluetoothDevice pairedDevice){
        String pairedAddress = pairedDevice.getAddress();
        pairedDevices.put(pairedAddress,pairedDevice);
        pairedDevicesAdapterData.add(pairedAddress);

        discoveredDevices.remove(pairedAddress);
        discoveredDevicesAdapterData.remove(pairedAddress);

        discoveredDevicesAdapter.updateList(discoveredDevicesAdapterData);
        pairedDevicesAdapter.updateList(pairedDevicesAdapterData);
    }

    private BroadcastReceiver bluetoothMsgReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String text = intent.getStringExtra("msg");
            if(receivedTextView.getText() == null){
                receivedTextView.setText(text);
            }else{
                receivedTextView.setText(receivedTextView.getText() + "\n"+text);
            }
        }
    };

    private BroadcastReceiver sendBluetoothReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String msg = intent.getStringExtra("msg");
            try{
                byte[] msgInBytes = msg.getBytes(Charset.defaultCharset());
                btConnectionService.write(msgInBytes);
            }catch(Exception e){
                Log.e(TAG,"An error occurred while sending bluetooth message");
                e.printStackTrace();
            }
        }
    };

    private BroadcastReceiver btConnectionUpdateReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            try{
                String status = intent.getStringExtra("msg");
                switch(status.toUpperCase()){
                    case "CONNECTED":
                        curConnectionBtn.setText("Disconnect");
                        break;
                    case "DISCONNECTED":
                        showShortToast("Bluetooth Connection disconnected");
                        if(retryConnection){
                            reconnectionHandler.postDelayed(reconnectRunnable, 5000);
                        }else {
                            curConnectionBtn.setText("Connect");
                        }
                        break;
                }
            }catch (Exception e){
                Log.e(TAG, "onReceive: An error occurred while trying to auto reconnect bluetooth");
                e.printStackTrace();
            }
        }
    };


}