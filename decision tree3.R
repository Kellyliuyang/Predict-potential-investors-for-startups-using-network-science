library(DMwR2)
library(readr)

train_data <- read.csv("/Users/yangliu/Documents/586 final project/train2017_2.csv")
test_data <- read.csv("/Users/yangliu/Documents/586 final project/test2018_2.csv")

train <- subset(train_data,select=c("state_code_x", "status","state_code_y","investor_type", "investment_count","funding_rounds","score","company_score_i","eigen_i","eigen_c","normalized_investment","label"))
test <- subset(test_data,select=c("state_code_x", "status","state_code_y","investor_type",  "investment_count","funding_rounds","score","company_score_i","eigen_i","eigen_c","normalized_investment","label"))
#train <- subset(train_data,select=c("state_code_x", "status","state_code_y","investor_type", "funding_rounds","investment_count","eigen_i","eigen_c","normalized_investment","label"))
#test <- subset(test_data,select=c("state_code_x", "status","state_code_y","investor_type",  "funding_rounds","investment_count","eigen_i","eigen_c","normalized_investment","label"))
#train <- subset(train_data,select=c("state_code_x", "status","state_code_y","investor_type", "investment_count","funding_rounds","score","company_score_i","normalized_investment","label"))
#test <- subset(test_data,select=c("state_code_x", "status","state_code_y","investor_type",  "investment_count","funding_rounds","score","company_score_i","normalized_investment","label"))
#train <- subset(train_data,select=c("state_code_x", "status","state_code_y", "investor_type", "investment_count","funding_rounds","label"))
#test <- subset(test_data,select=c("state_code_x", "status","state_code_y","investor_type","investment_count","funding_rounds","label"))
#,"funding_rounds"
head(train)
head(test)
#"score","company_score_i", "eigen_i","eigen_c","community","normalized_investment",
train$label <- as.factor(train$label)
test$label <- as.factor(test$label)
#build a tree
tree2 <- rpartXse(label~ ., train, se=0.5)
#use tree2 predict class label for test dataset
ps1 <- predict(tree2, test)
head(ps1)
#predict class label
predict <- predict(tree2, test, type="class")
#craete a contigency table to check the performance
result <- (cm <- table(test$label, predict))
result
recall <- result[2,2]/(result[2,2]+result[2,1])
recall
precision <- result[2,2]/(result[2,2]+result[1,2])
precision
F1 <- 2*precision*recall/(precision+recall)
F1
prp(tree2, type=1, extra=101, roundint = FALSE)
tree2


