import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  Dimensions,
  TouchableOpacity,
  Vibration,
} from 'react-native';
import { BarCodeScanner } from 'expo-barcode-scanner';
import { Camera } from 'expo-camera';
import { Ionicons } from '@expo/vector-icons';
import { Card, Title, Paragraph, Button, ActivityIndicator } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';

const { width, height } = Dimensions.get('window');

export default function BarcodeScannerScreen({ navigation }) {
  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [scannedData, setScannedData] = useState(null);
  const [productInfo, setProductInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCameraPermissions();
  }, []);

  const getCameraPermissions = async () => {
    const { status } = await Camera.requestCameraPermissionsAsync();
    setHasPermission(status === 'granted');
  };

  const handleBarCodeScanned = async ({ type, data }) => {
    if (scanned) return;
    
    setScanned(true);
    setScanning(false);
    Vibration.vibrate();
    
    try {
      setLoading(true);
      const productInfo = await fetchProductInfo(data);
      setScannedData(data);
      setProductInfo(productInfo);
    } catch (error) {
      Alert.alert('Error', 'Failed to fetch product information');
    } finally {
      setLoading(false);
    }
  };

  const fetchProductInfo = async (barcode) => {
    // Simulate API call - replace with actual API endpoint
    const response = await fetch(`/api/v1/products/search/${barcode}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getStoredToken()}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (response.ok) {
      return await response.json();
    } else {
      throw new Error('Product not found');
    }
  };

  const getStoredToken = () => {
    // In a real app, use AsyncStorage or secure storage
    return 'your-jwt-token-here';
  };

  const resetScanner = () => {
    setScanned(false);
    setScannedData(null);
    setProductInfo(null);
    setScanning(true);
  };

  const startScanning = () => {
    setScanning(true);
    setScanned(false);
  };

  if (hasPermission === null) {
    return (
      <View style={styles.centerContainer}>
        <Text>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.centerContainer}>
        <Ionicons name="camera-off" size={64} color="#666" />
        <Text style={styles.permissionText}>Camera permission is required</Text>
        <Button mode="contained" onPress={getCameraPermissions} style={styles.button}>
          Grant Permission
        </Button>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {scanning ? (
        <View style={styles.cameraContainer}>
          <BarCodeScanner
            onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
            style={StyleSheet.absoluteFillObject}
          />
          
          {/* Overlay */}
          <View style={styles.overlay}>
            <View style={styles.topOverlay} />
            <View style={styles.middleRow}>
              <View style={styles.sideOverlay} />
              <View style={styles.scanArea}>
                <View style={styles.scanFrame} />
              </View>
              <View style={styles.sideOverlay} />
            </View>
            <View style={styles.bottomOverlay} />
          </View>

          {/* Instructions */}
          <View style={styles.instructionsContainer}>
            <Text style={styles.instructionsText}>
              Position the barcode within the frame
            </Text>
          </View>

          {/* Controls */}
          <View style={styles.controlsContainer}>
            <TouchableOpacity
              style={styles.controlButton}
              onPress={() => setScanning(false)}
            >
              <Ionicons name="close" size={24} color="white" />
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.controlButton}
              onPress={resetScanner}
            >
              <Ionicons name="refresh" size={24} color="white" />
            </TouchableOpacity>
          </View>
        </View>
      ) : (
        <View style={styles.resultsContainer}>
          {loading ? (
            <View style={styles.centerContainer}>
              <ActivityIndicator size="large" color="#3B82F6" />
              <Text style={styles.loadingText}>Fetching product information...</Text>
            </View>
          ) : scannedData && productInfo ? (
            <Card style={styles.productCard}>
              <Card.Content>
                <Title>Product Found</Title>
                <Paragraph>Barcode: {scannedData}</Paragraph>
                <Paragraph>Name: {productInfo.name_en}</Paragraph>
                <Paragraph>Type: {productInfo.product_type}</Paragraph>
                <Paragraph>Unit: {productInfo.unit}</Paragraph>
                <Paragraph>Status: {productInfo.is_active ? 'Active' : 'Inactive'}</Paragraph>
              </Card.Content>
              <Card.Actions>
                <Button onPress={resetScanner}>Scan Again</Button>
                <Button mode="contained" onPress={() => navigation.navigate('Batches')}>
                  View Batches
                </Button>
              </Card.Actions>
            </Card>
          ) : scannedData ? (
            <Card style={styles.productCard}>
              <Card.Content>
                <Title>Product Not Found</Title>
                <Paragraph>Barcode: {scannedData}</Paragraph>
                <Paragraph>This product is not in our database.</Paragraph>
              </Card.Content>
              <Card.Actions>
                <Button onPress={resetScanner}>Scan Again</Button>
              </Card.Actions>
            </Card>
          ) : (
            <View style={styles.centerContainer}>
              <Ionicons name="qr-code" size={64} color="#3B82F6" />
              <Text style={styles.welcomeText}>Barcode Scanner</Text>
              <Text style={styles.descriptionText}>
                Scan product barcodes to view information and track batches
              </Text>
              <Button
                mode="contained"
                onPress={startScanning}
                style={styles.scanButton}
                icon="camera"
              >
                Start Scanning
              </Button>
            </View>
          )}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  cameraContainer: {
    flex: 1,
  },
  overlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
  },
  topOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  middleRow: {
    flexDirection: 'row',
    height: 200,
  },
  sideOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  scanArea: {
    width: 250,
    height: 200,
    justifyContent: 'center',
    alignItems: 'center',
  },
  scanFrame: {
    width: 200,
    height: 200,
    borderWidth: 2,
    borderColor: '#3B82F6',
    borderRadius: 10,
    backgroundColor: 'transparent',
  },
  bottomOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  instructionsContainer: {
    position: 'absolute',
    top: 100,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  instructionsText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  controlsContainer: {
    position: 'absolute',
    bottom: 50,
    left: 0,
    right: 0,
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  controlButton: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: 'rgba(0,0,0,0.6)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  resultsContainer: {
    flex: 1,
    padding: 20,
  },
  productCard: {
    marginVertical: 10,
    elevation: 4,
  },
  welcomeText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 20,
  },
  descriptionText: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginVertical: 20,
  },
  scanButton: {
    marginTop: 20,
  },
  permissionText: {
    fontSize: 18,
    color: '#666',
    textAlign: 'center',
    marginVertical: 20,
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  button: {
    marginTop: 20,
  },
});
