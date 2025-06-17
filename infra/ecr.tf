resource "aws_ecr_repository" "simplesim" {
  for_each = toset(["backend", "frontend"])
  name     = "simplesim-${each.value}"
}


