import { connectToDatabase } from "../../util/mongodb";

export default async (req, res) => {
    const { db } = await connectToDatabase();
    const mice = await db
      .collection("popularity")
      .find({})
      .sort({ count: -1 })
      .limit(20)
      .toArray();
  
    res.json(mice);
};