// Review screen for captured receipts with Supabase upload
// Upload flow: Supabase Storage → Edge Function → Odoo

import React, { useState } from 'react';
import { View, Text, Image, Button, StyleSheet, Alert, ActivityIndicator } from 'react-native';
import { uploadReceipt } from '../api/receipts';

interface ReviewScreenProps {
  route: {
    params: {
      photoUri: string;
      fileName: string;
      mimeType: string;
      fileSize: number;
    };
  };
  navigation: any;
}

export default function ReviewScreen({ route, navigation }: ReviewScreenProps) {
  const { photoUri, fileName, mimeType, fileSize } = route.params;
  const [uploading, setUploading] = useState(false);

  /**
   * Upload receipt to Supabase and notify Odoo
   */
  const handleSubmit = async () => {
    setUploading(true);
    try {
      const result = await uploadReceipt({
        fileUri: photoUri,
        fileName,
        mimeType,
        fileSize,
      });

      if (result.success) {
        Alert.alert(
          'Success',
          `Receipt uploaded! Odoo expense created (ID: ${result.odoo_expense_id}).`,
          [
            {
              text: 'OK',
              onPress: () => navigation.navigate('Home'),
            },
          ]
        );
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (error: any) {
      Alert.alert('Upload Failed', error.message);
    } finally {
      setUploading(false);
    }
  };

  /**
   * Retake photo
   */
  const handleRetake = () => {
    navigation.goBack();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Review Receipt</Text>

      <Image source={{ uri: photoUri }} style={styles.preview} resizeMode="contain" />

      <Text style={styles.info}>
        File: {fileName}
        {'\n'}
        Size: {(fileSize / 1024).toFixed(2)} KB
        {'\n'}
        Type: {mimeType}
      </Text>

      {uploading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Uploading to Supabase...</Text>
          <Text style={styles.loadingSubtext}>Notifying Odoo...</Text>
        </View>
      ) : (
        <View style={styles.buttonContainer}>
          <View style={styles.button}>
            <Button title="Retake Photo" onPress={handleRetake} color="#999" />
          </View>
          <View style={styles.button}>
            <Button title="Submit Receipt" onPress={handleSubmit} />
          </View>
        </View>
      )}

      <Text style={styles.help}>
        Receipt will be uploaded to Supabase Storage{'\n'}
        and automatically processed by Odoo.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 20,
  },
  preview: {
    width: '100%',
    height: 400,
    borderRadius: 8,
    marginBottom: 20,
    backgroundColor: '#f5f5f5',
  },
  info: {
    fontSize: 14,
    color: '#666',
    marginBottom: 20,
    textAlign: 'center',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  button: {
    flex: 1,
    marginHorizontal: 5,
  },
  loadingContainer: {
    alignItems: 'center',
    marginVertical: 40,
  },
  loadingText: {
    marginTop: 15,
    fontSize: 16,
    fontWeight: '600',
  },
  loadingSubtext: {
    marginTop: 5,
    fontSize: 14,
    color: '#666',
  },
  help: {
    textAlign: 'center',
    color: '#999',
    fontSize: 12,
    marginTop: 20,
  },
});
