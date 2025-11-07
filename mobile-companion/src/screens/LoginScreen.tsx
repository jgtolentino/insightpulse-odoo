// Login screen using Supabase Auth (Magic Link + OAuth)
// Supports email magic link and Google/Apple OAuth providers

import React, { useState } from 'react';
import { View, TextInput, Button, Text, StyleSheet, Alert, Platform } from 'react-native';
import { supabase } from '../supabase/client';

export default function LoginScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  /**
   * Send magic link to email
   * User receives email with login link
   */
  const handleMagicLinkLogin = async () => {
    if (!email) {
      Alert.alert('Error', 'Please enter your email address');
      return;
    }

    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithOtp({
        email,
        options: {
          emailRedirectTo: Platform.OS === 'web'
            ? window.location.origin
            : 'insightpulse://login',
        },
      });

      if (error) {
        throw error;
      }

      Alert.alert(
        'Check your email',
        `We sent a magic link to ${email}. Click the link to sign in.`,
        [{ text: 'OK' }]
      );
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  /**
   * OAuth login (Google, Apple)
   * Only works on web - native requires additional setup
   */
  const handleOAuthLogin = async (provider: 'google' | 'apple') => {
    if (Platform.OS !== 'web') {
      Alert.alert('Not Available', 'OAuth is only available on web version. Use magic link for mobile.');
      return;
    }

    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: window.location.origin,
        },
      });

      if (error) {
        throw error;
      }
    } catch (error: any) {
      Alert.alert('Error', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>InsightPulse Expense Companion</Text>
      <Text style={styles.subtitle}>Sign in to upload receipts</Text>

      <TextInput
        style={styles.input}
        placeholder="Enter your email"
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        editable={!loading}
      />

      <Button
        title={loading ? 'Sending...' : 'Send Magic Link'}
        onPress={handleMagicLinkLogin}
        disabled={loading}
      />

      {Platform.OS === 'web' && (
        <>
          <Text style={styles.divider}>OR</Text>

          <Button
            title="Sign in with Google"
            onPress={() => handleOAuthLogin('google')}
            disabled={loading}
          />

          <View style={styles.spacing} />

          <Button
            title="Sign in with Apple"
            onPress={() => handleOAuthLogin('apple')}
            disabled={loading}
          />
        </>
      )}

      <Text style={styles.help}>
        First time? Create your account by signing in with your email.
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#fff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 30,
    color: '#666',
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    padding: 15,
    borderRadius: 8,
    marginBottom: 20,
    fontSize: 16,
  },
  divider: {
    textAlign: 'center',
    marginVertical: 20,
    color: '#999',
  },
  spacing: {
    height: 10,
  },
  help: {
    textAlign: 'center',
    marginTop: 30,
    color: '#666',
    fontSize: 14,
  },
});
