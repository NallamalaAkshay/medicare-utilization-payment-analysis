data <- read.csv("output/office_visit_99213_by_state_2024.csv")

# Match the 100,000-service threshold used in Tableau.
data <- subset(data, services >= 100000)

payments <- data$avg_medicare_payment_per_service

cat("Areas analyzed:", nrow(data), "\n")
cat("Median payment: $", round(median(payments), 2), "\n", sep = "")
cat("25th percentile: $", round(unname(quantile(payments, 0.25)), 2), "\n", sep = "")
cat("75th percentile: $", round(unname(quantile(payments, 0.75)), 2), "\n", sep = "")
cat("Lowest: ", data$state[which.min(payments)],
    " ($", round(min(payments), 2), ")\n", sep = "")
cat("Highest: ", data$state[which.max(payments)],
    " ($", round(max(payments), 2), ")\n", sep = "")

# Descriptive association across state-level summaries.
rho <- cor(data$services, payments, method = "spearman")
cat("Spearman correlation (volume vs payment): ",
    round(rho, 3), "\n", sep = "")

png("output/payment_distribution_2024.png", width = 1000, height = 650)
hist(payments,
     main = "Payment per service across areas: HCPCS 99213",
     xlab = "Average Medicare payment per service ($)",
     col = "#4E79A7",
     border = "white")
abline(v = median(payments), col = "#D62728", lwd = 3)
legend("topright", "Median", col = "#D62728", lwd = 3, bty = "n")
dev.off()