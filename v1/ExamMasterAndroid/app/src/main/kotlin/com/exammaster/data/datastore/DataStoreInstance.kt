package com.exammaster.data.datastore

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.preferencesDataStore

/**
 * 统一的DataStore实例
 * 确保整个应用程序使用同一个DataStore
 */
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "exam_master_preferences")
