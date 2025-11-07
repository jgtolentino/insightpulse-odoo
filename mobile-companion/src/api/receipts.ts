// Receipt upload API using Supabase Storage and Edge Functions
// Architecture: Upload to Supabase → Edge Function mints signed URL → Notifies Odoo

import { supabase, getCurrentUser } from '../supabase/client';

interface UploadReceiptParams {
  fileUri: string; // Native: file:// URI, Web: blob URL
  fileName: string;
  mimeType: string;
  fileSize: number;
}

interface UploadReceiptResult {
  success: boolean;
  receipt_id?: string;
  odoo_expense_id?: number;
  error?: string;
}

/**
 * Upload receipt to Supabase Storage and notify Odoo
 * @param params - Receipt file details
 * @returns Upload result with receipt ID and Odoo expense ID
 */
export const uploadReceipt = async (params: UploadReceiptParams): Promise<UploadReceiptResult> => {
  try {
    // Step 1: Get current user
    const user = await getCurrentUser();
    if (!user) {
      throw new Error('User not authenticated');
    }

    // Step 2: Prepare file for upload
    // Native: Convert file:// URI to blob
    // Web: Use blob directly
    const response = await fetch(params.fileUri);
    const blob = await response.blob();

    // Step 3: Upload to Supabase Storage (private bucket with RLS)
    // File path: {user_id}/{timestamp}_{filename}
    const timestamp = Date.now();
    const filePath = `${user.id}/${timestamp}_${params.fileName}`;

    const { error: uploadError } = await supabase.storage
      .from('receipts')
      .upload(filePath, blob, {
        contentType: params.mimeType,
        cacheControl: '3600',
        upsert: false,
      });

    if (uploadError) {
      throw new Error(`Upload failed: ${uploadError.message}`);
    }

    console.log(`[uploadReceipt] File uploaded: ${filePath}`);

    // Step 4: Invoke Edge Function to notify Odoo
    const { data, error: functionError } = await supabase.functions.invoke('notify-odoo', {
      body: {
        file_path: filePath,
        user_id: user.id,
        file_name: params.fileName,
        mime_type: params.mimeType,
        file_size: params.fileSize,
      },
    });

    if (functionError) {
      throw new Error(`Edge Function failed: ${functionError.message}`);
    }

    console.log(`[uploadReceipt] Odoo notified. Expense ID: ${data.odoo_expense_id}`);

    return {
      success: true,
      receipt_id: data.receipt_id,
      odoo_expense_id: data.odoo_expense_id,
    };
  } catch (error: any) {
    console.error('[uploadReceipt] Error:', error);
    return {
      success: false,
      error: error.message,
    };
  }
};

/**
 * Get user's receipt history
 * @returns List of receipts with metadata
 */
export const getReceiptHistory = async () => {
  const user = await getCurrentUser();
  if (!user) {
    throw new Error('User not authenticated');
  }

  const { data, error } = await supabase
    .from('receipts')
    .select('*')
    .eq('user_id', user.id)
    .order('uploaded_at', { ascending: false })
    .limit(50);

  if (error) {
    throw new Error(`Failed to fetch receipts: ${error.message}`);
  }

  return data;
};

/**
 * Get receipt details by ID
 * @param receiptId - Receipt UUID
 * @returns Receipt details
 */
export const getReceiptById = async (receiptId: string) => {
  const user = await getCurrentUser();
  if (!user) {
    throw new Error('User not authenticated');
  }

  const { data, error } = await supabase
    .from('receipts')
    .select('*')
    .eq('id', receiptId)
    .eq('user_id', user.id)
    .single();

  if (error) {
    throw new Error(`Failed to fetch receipt: ${error.message}`);
  }

  return data;
};
