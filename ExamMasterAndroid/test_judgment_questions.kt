import com.exammaster.data.database.entities.Question

fun main() {
    // 创建一个判断题实例
    val judgmentQuestion = Question(
        id = "test1",
        stem = "正确反映和把握价值关系，需要对"主体"进行区分，需要处理好个体评价标准和社会评价标准之间的关系。",
        answer = "正确",
        difficulty = "无",
        qtype = "判断题",
        category = "测试",
        options = "", // 空选项，模拟CSV数据
        createdAt = System.currentTimeMillis().toString()
    )
    
    // 测试getFormattedOptions方法
    val options = judgmentQuestion.getFormattedOptions()
    println("判断题选项:")
    options.forEach { (key, value) ->
        println("$key: $value")
    }
    
    // 验证选项不为空
    println("\n选项是否为空: ${options.isEmpty()}")
    println("选项数量: ${options.size}")
    
    // 创建一个多选题作为对比
    val multipleChoiceQuestion = Question(
        id = "test2",
        stem = "毛泽东思想产生的社会历史条件有()。",
        answer = "ABCD",
        difficulty = "无",
        qtype = "多选题",
        category = "测试",
        options = """{"A":"十月革命开辟的世界无产阶级革命的新时代","B":"近代中国社会矛盾和革命运动的发展"}""",
        createdAt = System.currentTimeMillis().toString()
    )
    
    val multipleOptions = multipleChoiceQuestion.getFormattedOptions()
    println("\n多选题选项:")
    multipleOptions.forEach { (key, value) ->
        println("$key: $value")
    }
}
