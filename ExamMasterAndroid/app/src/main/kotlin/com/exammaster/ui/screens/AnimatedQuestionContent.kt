package com.exammaster.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedContentTransitionScope
import androidx.compose.animation.SizeTransform
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.animation.with
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier

/**
 * 带有动画效果的题目内容组件
 * 
 * @param targetState 当前要显示的内容状态（通常是题目ID或索引）
 * @param modifier Modifier修饰符
 * @param content 内容组合函数
 */
@Composable
fun <T> AnimatedQuestionContent(
    targetState: T,
    modifier: Modifier = Modifier,
    content: @Composable (T) -> Unit
) {
    // 记住上一个状态，用于判断动画方向
    var lastState: T? = remember { null }
    
    AnimatedContent(
        targetState = targetState,
        transitionSpec = {
            // 默认向左滑动（下一题）
            val direction = AnimatedContentTransitionScope.SlideDirection.Left
            
            // 简化的滑动动画
            slideIntoContainer(
                towards = direction,
                animationSpec = tween(300)
            ) togetherWith
            slideOutOfContainer(
                towards = direction,
                animationSpec = tween(300)
            ) using SizeTransform(clip = false)
        },
        modifier = modifier,
        label = "question_animation"
    ) { state ->
        lastState = state
        content(state)
    }
} 