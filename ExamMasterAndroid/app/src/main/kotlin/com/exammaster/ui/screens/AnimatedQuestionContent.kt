package com.exammaster.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.EnterTransition
import androidx.compose.animation.ExitTransition
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier

/**
 * 封装题目切换动画效果的组件
 * 
 * @param targetState 当前题目的状态，通常是题目ID
 * @param modifier 应用于动画容器的修饰符
 * @param transitionDuration 动画持续时间（毫秒）
 * @param content 基于目标状态渲染的内容
 */
@OptIn(ExperimentalAnimationApi::class)
@Composable
fun <T> AnimatedQuestionContent(
    targetState: T,
    modifier: Modifier = Modifier,
    transitionDuration: Int = 300,
    content: @Composable (T) -> Unit
) {
    // 存储当前和前一个状态
    var currentState by remember { mutableStateOf(targetState) }
    var previousState by remember { mutableStateOf<T?>(null) }
    
    // 存储导航方向 (1 = 向前, -1 = 向后, 0 = 初始)
    var direction by remember { mutableStateOf(0) }
    
    // 当目标状态变化时，更新方向和状态
    LaunchedEffect(targetState) {
        if (previousState == null) {
            // 首次加载
            direction = 0
        } else if (targetState.toString() != currentState.toString()) {
            // 判断方向 - 这里我们使用 toString 来比较，更加可靠
            // 如果是数字类型的ID或者有序字符串，可以直接比较
            try {
                // 尝试作为数字比较
                val prev = previousState.toString().toDoubleOrNull()
                val curr = currentState.toString().toDoubleOrNull()
                val next = targetState.toString().toDoubleOrNull()
                
                if (prev != null && curr != null && next != null) {
                    direction = if (next > curr) 1 else -1
                } else {
                    // 作为字符串比较长度
                    val prevLen = previousState.toString().length
                    val currLen = currentState.toString().length
                    val nextLen = targetState.toString().length
                    direction = if (nextLen > currLen) 1 else -1
                }
            } catch (e: Exception) {
                // 默认向前
                direction = 1
            }
        }

        // 更新状态
        previousState = currentState
        currentState = targetState
    }
    
    // 构建进入退出动画 - 简化以减少闪屏
    val enterTransition = when (direction) {
        1, -1 -> fadeIn(tween(150)) // 只使用淡入效果，缩短动画时间
        else -> EnterTransition.None // 首次加载无动画
    }
    
    val exitTransition = when (direction) {
        1, -1 -> fadeOut(tween(150)) // 只使用淡出效果，缩短动画时间
        else -> ExitTransition.None // 首次加载无动画
    }
    
    AnimatedContent(
        targetState = targetState,
        modifier = modifier,
        transitionSpec = { enterTransition togetherWith exitTransition },
        label = "questionAnimatedContent"
    ) { state ->
        content(state)
    }
} 