import {
    Card,
    Title,
    Pagination,
    CardList,
    Container,
    Main,
    CheckboxGroup,
    Input,
} from "../../components"
import styles from "./styles.module.css"
import { useRecipes } from "../../utils/index.js"
import { useEffect, useState } from "react"
import api from "../../api"
import MetaTags from "react-meta-tags"

const HomePage = ({ updateOrders }) => {
    const {
        recipes,
        setRecipes,
        recipesCount,
        setRecipesCount,
        recipesPage,
        setRecipesPage,
        tagsValue,
        setTagsValue,
        handleTagsChange,
        handleLike,
        handleAddToCart,
    } = useRecipes()

    const [recipeValue, setRecipeValue] = useState("")

    const getRecipes = ({ page = 1, tags, name }) => {
        api.getRecipes({ page, tags, name }).then((res) => {
            const { results, count } = res
            setRecipes(results)
            setRecipesCount(count)
        })
    }

    useEffect(
        (_) => {
            getRecipes({
                page: recipesPage,
                tags: tagsValue,
                name: recipeValue,
            })
        },
        [recipesPage, tagsValue, recipeValue]
    )

    useEffect((_) => {
        api.getTags().then((tags) => {
            setTagsValue(tags.map((tag) => ({ ...tag, value: true })))
        })
    }, [])

    return (
        <Main>
            <Container>
                <MetaTags>
                    <title>Рецепты</title>
                    <meta
                        name="description"
                        content="Продуктовый помощник - Рецепты"
                    />
                    <meta property="og:title" content="Рецепты" />
                </MetaTags>
                <div className={styles.title}>
                    <Title title="Рецепты" />
                    <CheckboxGroup
                        values={tagsValue}
                        handleChange={(value) => {
                            setRecipesPage(1)
                            handleTagsChange(value)
                        }}
                    />
                </div>
                <div className={styles.ingredients}>
                    <div className={styles.ingredientsInputs}>
                        <Input
                            label="Поиск рецепта"
                            className={styles.ingredientsNameInput}
                            inputClassName={styles.ingredientsInput}
                            labelClassName={styles.ingredientsLabel}
                            onChange={(e) => {
                                const value = e.target.value
                                setRecipeValue(value)
                            }}
                            // onFocus={(_) => {
                            //     setShowIngredients(true)
                            // }}
                            value={recipeValue}
                        />
                    </div>
                </div>
                <CardList>
                    {recipes.map((card) => (
                        <Card
                            {...card}
                            key={card.id}
                            updateOrders={updateOrders}
                            handleLike={handleLike}
                            handleAddToCart={handleAddToCart}
                        />
                    ))}
                </CardList>
                <Pagination
                    count={recipesCount}
                    limit={6}
                    page={recipesPage}
                    onPageChange={(page) => setRecipesPage(page)}
                />
            </Container>
        </Main>
    )
}

export default HomePage
